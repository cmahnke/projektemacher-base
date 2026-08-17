#!/usr/bin/env python

import os, io, re, yaml, toml, sys, base64
from termcolor import cprint
from PIL import Image, ImageFont, ImageDraw, UnidentifiedImageError
import xml.etree.ElementTree as ET
from pathlib import Path
import tempfile

try:
    import pyvips
except ImportError:
    pyvips = None

configFile = "./config/_default/config.toml"
contentPath = "./content"
filePattern = "(_?)index(\\.([a-zA-Z-]){2,5})?\\.md"
maxImageDimension = 17500

namespaces = {
    "svg": "http://www.w3.org/2000/svg",
    "xlink": "http://www.w3.org/1999/xlink",
}

Image.MAX_IMAGE_PIXELS = maxImageDimension * maxImageDimension


# TODO: Move to PyHugo
def loadConfig(configFile):
    config = toml.load(configFile)
    if "preview" in config["params"]:
        return config["params"]["preview"]
    else:
        return


# TODO: Move to PyHugo
def readMetadata(file):
    post = io.open(file, mode="r", encoding="utf-8").read()
    header = re.sub(r"^---$.(.*?)^---$.*", "\\1", post, count=0, flags=re.MULTILINE | re.DOTALL)
    try:
        post = yaml.load(header, Loader=yaml.FullLoader)
    except yaml.YAMLError as exc:
        if hasattr(exc, "problem_mark"):
            mark = exc.problem_mark
            cprint(
                "Error in {} position: ({}:{})".format(file, mark.line + 1, mark.column + 1),
                "red",
            )
    except Exception as inst:
        cprint("Error in %s".format(file), "red")

    if "params" in post:
        for key in post["params"]:
            post[key] = post["params"][key]

    return post


def loadImageAsPNGBytes(path):
    """
    Load any image libvips understands (including formats PIL can't read,
    e.g. JXL) and return it re-encoded as PNG bytes, entirely in memory.
    """
    if pyvips is None:
        raise RuntimeError("pyvips is not available")
    vipsImage = pyvips.Image.new_from_file(path, access="sequential")
    return vipsImage.write_to_buffer(".png")


def loadPILImage(path):
    """
    Return a PIL.Image for `path`. If PIL can't decode it directly (e.g. JXL),
    fall back to pyvips to convert it in-memory to PNG bytes first.
    No temporary files are created.
    """
    try:
        img = Image.open(path)
        img.load()
        return img
    except (UnidentifiedImageError, OSError):
        pngBytes = loadImageAsPNGBytes(path)
        return Image.open(io.BytesIO(pngBytes))


def drawTitle(title, file, config):
    font = ImageFont.truetype(config["font"]["location"], config["font"]["size"])
    img = Image.new("RGBA", (config["size"]["width"], config["size"]["height"]), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), title, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((15, 15), title, fill=config["font"]["color"], font=font)
    img.save(file)


def drawSVG(title, contentFile, outFile, config):
    global namespaces
    path = os.path.dirname(contentFile)
    template = config["svg"]["template"]
    templateBase = os.path.dirname(template)
    # Python has an incomplete XML implementation :( https://stackoverflow.com/questions/44282975/how-to-access-attribute-value-in-xml-containing-namespace-using-elementtree-in-p
    xlinkAttr = "{" + namespaces["xlink"] + "}" + "href"
    previewImg = getPreviewImg(config, contentFile)
    cprint(f"Rendering '{outFile}' from '{template}', preview '{previewImg}'", "yellow")

    svgTree = ET.parse(template)

    # Set paths relative to output dir
    for styleElem in svgTree.findall(".//svg:style", namespaces):
        style = styleElem.text
        if style == "" or style is None:
            cprint(f"No style in {template}", 'red')
            continue
        for urlMatch, url in re.findall(r"(url\s*?$[\'\"]?(.*?)[\'\"]?$)", style, re.S | re.M):
            relLocation = os.path.normpath(os.path.join(templateBase, os.path.dirname(url)))
            targetPath = os.path.relpath(relLocation, os.path.dirname(outFile))
            newLocation = os.path.join(targetPath, os.path.basename(url))
            style = style.replace(urlMatch, "url('" + newLocation + "')")
        styleElem.text = style

    for linkElem in svgTree.findall(".//*[@xlink:href]", namespaces):
        link = linkElem.get(xlinkAttr)
        relLocation = os.path.normpath(os.path.join(templateBase, os.path.dirname(link)))
        targetPath = os.path.relpath(relLocation, os.path.dirname(outFile))
        newLocation = os.path.join(targetPath, os.path.basename(link))
        linkElem.set(xlinkAttr, newLocation)

    # Update image
    imageXPath = ".//*[@id = 'preview-image']"

    if previewImg is False:
        return
    if config["source"] == "post" and previewImg != "":
        previewImg = os.path.join(path, previewImg)

    previewElem = None

    if previewImg != "" and os.path.isfile(previewImg):
        if str(previewImg).lower().endswith(".jxl"):
            if pyvips is None:
                cprint("pyvips isn't installed, can't process JXL preview image, skipping!", "red")
                return
            cprint(
                f"Preview image '{previewImg}' is JXL, converting in-memory via pyvips (no temp files)",
                "yellow",
            )
            try:
                pngBytes = loadImageAsPNGBytes(previewImg)
            except Exception as e:
                cprint(f"Can't convert JXL image '{previewImg}' with pyvips: {e}", "red")
                return
            b64 = base64.b64encode(pngBytes).decode("ascii")
            previewSrc = f"data:image/png;base64,{b64}"
        else:
            previewSrc = os.path.join(
                os.path.relpath(os.path.dirname(previewImg), os.path.dirname(outFile)),
                os.path.basename(previewImg),
            )
        cprint("Setting @id='preview-image' to '{}'".format(previewImg), "yellow")
        if svgTree.findall(imageXPath, namespaces):
            previewElem = svgTree.findall(imageXPath, namespaces)[0]
            previewElem.set(xlinkAttr, previewSrc)
    elif "removeMissing" in config["svg"]:
        if config["svg"]["removeMissing"] == True:
            parents = svgTree.findall(imageXPath + "/..", namespaces)
            if len(parents) > 0:
                parent = parents[0]
                previewElem = svgTree.findall(imageXPath, namespaces)[0]
                parent.remove(previewElem)
                cprint(f"Removed reference to missing image '{previewImg}'", "yellow")
                previewElem = None
            else:
                cprint(
                    "Can't find parent for missing preview image from template '{}'".format(template),
                    "yellow",
                )

    else:
        cprint("Image '{}' dosn't exit, ignoring".format(previewImg), "red")

    # TODO: This currently only scales to width
    # TODO: This currenly only centres
    if previewImg != "" and previewElem is not None and "scale" in config["svg"]:
        try:
            img = loadPILImage(previewImg)
        except FileNotFoundError:
            cprint(f"Can't find image file '{previewImg}', skipping!", "red")
            return
        except Image.DecompressionBombError:
            cprint(f"Can't load image file '{previewImg}' since it's to large, skipping!", "red")
            return
        except UnidentifiedImageError:
            cprint(f"Can't load image file '{previewImg} since the format isn't recognized', skipping!", "red")
            return
        imgWidth, imgHeight = img.size

        if config["svg"]["scale"] == "width":
            scale = int(previewElem.get("height")) / imgHeight
            scaleWidth = imgWidth * scale
            scaleX = int(previewElem.get("x")) + (int(previewElem.get("width")) - scaleWidth) / 2
            previewElem.set("x", str(scaleX))
            previewElem.set("width", str(scaleWidth))
        elif config["svg"]["scale"] == "height":
            raise NotImplementedError

    # Update text
    svgTree.findall(".//*[@id = 'text-container']", namespaces)[0].text = title

    cprint("Writing {}".format(outFile), "green")
    svgTree.write(outFile)


def drawPNG(title, file, config):
    drawTitle(title, output, config)


def getPreviewImg(config, contentFile):
    path = os.path.dirname(contentFile)
    if config["source"] == "file" or config["source"] == "image":
        return os.path.join(path, config["image"])
    elif config["source"] == "overlay":
        return ""
    elif config["source"] == "post":
        metadata = readMetadata(contentFile)
        if "preview" in metadata:
            #preview = os.path.join(path, metadata["preview"])
            preview = metadata["preview"]
            if isinstance(preview, dict) and "image" in preview:
                preview = preview["image"]
            cprint(f"Using {preview} as preview", 'yellow')
            if "." in preview:
                return preview
        if "cover" in metadata:
            #preview = os.path.join(path, metadata["preview"])
            preview = metadata["cover"]
            if isinstance(preview, list) and preview[0]:
                preview = preview[0]
            cprint(f"Using {preview} as preview", 'yellow')
            return preview
        if "resources" in metadata:
            preview = metadata["resources"]
            if isinstance(preview, list) and "src" in preview[0]:
                preview = preview[0]["src"]
            cprint(f"Using {preview} as preview", 'yellow')
            return preview

        else:
            return ""
    else:
        cprint("Unknown source type: '{}'".format(config["source"]), "red")
        return False


if sys.version_info[0] < 3 or sys.version_info[1] < 13:
    raise Exception("Must be using Python 3.13")

config = loadConfig(open(configFile, "r"))
if config is None:
    cprint("Preview is not configured!", "red")
    exit(0)

cFilePAttern = re.compile(filePattern)
for subdir, dirs, files in os.walk(contentPath):
    for file in files:
        fileMatch = cFilePAttern.match(file)
        if fileMatch:
            cprint("Processing " + os.path.join(subdir, file), "green")
            lang = fileMatch.group(2)
            contentFile = os.path.join(subdir, file)
            metadata = readMetadata(contentFile)
            if not "title" in metadata:
                cprint(
                    "No title in " + subdir + "/" + file + ", setting empty string.",
                    "red",
                )
                metadata["title"] = ""
            outputFileSuffix = config["outputPrefix"]
            if lang:
                outputFileSuffix += lang
            if config["format"] == "svg":
                output = os.path.join(subdir, outputFileSuffix + ".svg")
                drawSVG(metadata["title"], contentFile, output, config)
            elif config["format"] == "png":
                output = os.path.join(subdir, outputFileSuffix + ".png")
                drawPNG(metadata["title"], output, config)
            else:
                cprint(
                    "Can' process " + os.path.join(subdir, file) + ", no format set",
                    "red",
                )
