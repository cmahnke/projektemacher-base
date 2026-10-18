#!/usr/bin/env python

import sys, os, io, pathlib, re, argparse
from pprint import pprint
from math import floor
from datetime import datetime

# Doesn't work with Python 3.10
# from datetime import UTC
from fpdf import FPDF
from fpdf import FPDF_VERSION
from PIL import Image, UnidentifiedImageError
from termcolor import cprint
import pikepdf

try:
    import pyvips
except (ImportError, OSError):
    pyvips = None

sys.path.append(os.path.dirname(__file__))
from PyHugo import Post, Content

PDF_DPI = 300
TRANSCODE = True
DEFAULT_IN_DPI = 600


def resource_page_number(name: str, resources: list):
    for i, r in enumerate(resources):
        src = os.path.basename(str(r.get("src", "")))
        if os.path.splitext(src)[0] == name:
            return i
        iiif = r.get("params", {}).get("iiif")
        if iiif:
            base = os.path.basename(str(iiif).rstrip("/"))
            if os.path.splitext(base)[0] == name:
                return i
            parent = os.path.basename(os.path.dirname(str(iiif).rstrip("/")))
            if parent and os.path.splitext(parent)[0] == name:
                return i
    return None


def structure_title(entry: dict):
    label = entry.get("label")
    if isinstance(label, dict) and label:
        values = list(label.values())[0]
        if values:
            return str(values[0])
    return None


def parse_structure(entries, resources: list) -> list:
    outline = []
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        if entry.get("id") is not None or entry.get("type") is not None:
            cprint(
                f"Skipping legacy structure entry with id/type '{entry.get('id', entry.get('type'))}', "
                "use the label/page/items shorthand",
                "yellow",
            )
            continue
        title = structure_title(entry)
        if title is None:
            cprint(f"Skipping structure entry without label: {entry.get('page', '?')}", "yellow")
            continue
        page = None
        children = []
        ref = entry.get("page")
        if ref is not None:
            number = resource_page_number(str(ref), resources)
            if number is None:
                cprint(f"Page reference not found in resources: {ref}", "yellow")
            else:
                page = number
        for child in entry.get("items") or []:
            if not isinstance(child, dict):
                continue
            children.extend(parse_structure([child], resources))
        outline.append({"title": title, "page": page, "children": children})
    return outline


def outline_items(nodes: list) -> list:
    items = []
    for node in nodes:
        if node["page"] is not None:
            item = pikepdf.OutlineItem(node["title"], node["page"], pikepdf.PageLocation.Fit)
        else:
            item = pikepdf.OutlineItem(node["title"])
        if node["children"]:
            item.children.extend(outline_items(node["children"]))
        items.append(item)
    return items


def scale_image(image: Image, dpi: int):
    if "dpi" in image.info:
        in_dpi = image.info["dpi"][0]
        width = floor((image.size[0] / image.info["dpi"][0]) * dpi)
        height = floor((image.size[1] / image.info["dpi"][1]) * dpi)
    else:
        in_dpi = DEFAULT_IN_DPI
        width = floor((image.size[0] / DEFAULT_IN_DPI) * dpi)
        height = floor((image.size[1] / DEFAULT_IN_DPI) * dpi)
    cprint(
        f"Resizing from {image.size[0]}x{image.size[1]} to {width}x{height} (from {in_dpi}dpi to {dpi}dpi)",
        "yellow",
    )
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    image.info["dpi"] = (dpi, dpi)
    return image


# See https://py-pdf.github.io/fpdf2/Metadata.html
def add_metadata(file, metadata, labels=None, toc=None):
    with pikepdf.open(file, allow_overwriting_input=True) as pdf:
        with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:
            meta["dc:title"] = metadata["title"]
            meta["dc:description"] = metadata["description"]
            if "author" in metadata:
                meta["dc:creator"] = metadata["author"]
            meta["pdf:Producer"] = f"py-pdf/fpdf{FPDF_VERSION}"
            meta["xmp:CreatorTool"] = __file__
            meta["xmp:MetadataDate"] = datetime.now(datetime.utcnow().astimezone().tzinfo).isoformat()
            # Doesn't work with Python 3.10
            # meta["xmp:MetadataDate"] = datetime.now(UTC).isoformat()
            if "issueYear" in metadata:
                meta["dc:date"] = [str(metadata["issueYear"])]
            elif "year" in metadata:
                meta["dc:date"] = [str(metadata["year"])]
        if labels is not None:
            try:
                pdf.Root.PageLabels
            except:
                nt = pikepdf.NumberTree.new(pdf)
                pdf.Root.PageLabels = nt.obj

            pagelabels = pikepdf.NumberTree(pdf.Root.PageLabels)
            for i in range(len(labels)):
                if labels[i] is None:
                    pagelabels[i] = pikepdf.Dictionary()
                elif isinstance(labels[i], int):
                    pagelabels[i] = pikepdf.Dictionary(S=pikepdf.Name.D, St=labels[i])
                elif isinstance(labels[i], str):
                    if labels[i] == "uncounted":
                        pagelabels[i] = pikepdf.Dictionary()
                    else:
                        pagelabels[i] = pikepdf.Dictionary(P=labels[i])
                else:
                    raise NotImplementedError
        if toc:
            with pdf.open_outline() as outline:
                outline.root.extend(outline_items(toc))
        pdf.save()


def loadPILImage(path):
    """Load an image with PIL, falling back to pyvips for formats PIL can't decode (e.g. JXL)."""
    try:
        img = Image.open(path)
        img.load()
        return img
    except (UnidentifiedImageError, OSError):
        if pyvips is None:
            raise UnidentifiedImageError(f"Can't decode '{path}' with PIL and pyvips isn't installed")
        pngBytes = pyvips.Image.new_from_file(str(path), access="sequential").write_to_buffer(".png")
        return Image.open(io.BytesIO(pngBytes))


def image_to_pdf(pdf: FPDF, image: pathlib.Path) -> None:
    def px_to_mm(px: float, px_in_inch=72) -> float:
        mm_in_inch = 25.4
        inch = px / px_in_inch
        mm = inch * mm_in_inch
        return mm

    cover = loadPILImage(image)
    width: float
    height: float
    width, height = cover.size
    if "dpi" in cover.info:
        dpi = cover.info["dpi"][0]
        width, height = px_to_mm(width, cover.info["dpi"][0]), px_to_mm(height, cover.info["dpi"][1])
    else:
        cprint(f"DPI not set assuming {DEFAULT_IN_DPI}", "red")
        width, height = px_to_mm(width, DEFAULT_IN_DPI), px_to_mm(height, DEFAULT_IN_DPI)
        dpi = DEFAULT_IN_DPI
    cprint(f"Page size is {width}mm x {height}mm", "yellow")
    pdf.add_page(format=(width, height))
    if dpi == PDF_DPI:
        if not TRANSCODE:
            pdf.image(image, x=0, y=0, w=width, h=height)
        else:
            pdf.image(cover, x=0, y=0, w=width, h=height)
    else:
        cover = scale_image(cover, PDF_DPI)
        pdf.image(cover, x=0, y=0, w=width, h=height)

    cover.close()


def processSingle(post: Post, out: pathlib.Path):
    cprint(f"Starting to assemble {out}", "green")
    metadata = post.getMetadata()
    path = post.path
    if not "title" in metadata:
        raise ValueError(f"No title in post for {out}")
    else:
        title = metadata["title"]
    description = ""
    if "description" in metadata:
        description = metadata["description"]

    pdf_metadata = metadata
    if "params" in metadata and "iiif" in metadata["params"]:
        additional_metadata = metadata["params"]["iiif"]
        pdf_metadata = metadata | additional_metadata
    structure = None
    if isinstance(metadata.get("iiif"), dict):
        structure = metadata["iiif"].get("structure")
    elif isinstance(metadata.get("params"), dict) and isinstance(metadata["params"].get("iiif"), dict):
        structure = metadata["params"]["iiif"].get("structure")
    toc = parse_structure(structure, metadata.get("resources", [])) if structure else None
    if "resources" in metadata:
        pdf = FPDF(unit="mm")
        if TRANSCODE:
            pdf.set_compression(True)
            pdf.set_image_filter("DCTDecode")
        labels = []
        for r in metadata["resources"]:
            file = os.path.join(path, r["src"])

            try:
                label = int(re.findall(r"\d+", r["src"])[0])
            except:
                label = None
            if label == 0:
                label = None

            if "label" in r["params"]:
                label = r["params"]["label"]
            labels.append(label)
            cprint(f"Adding page {label} from {file}", "yellow")
            try:
                image_to_pdf(pdf, file)
            except FileNotFoundError as e:
                cprint(f"File not found: {e.filename}!", "red")
            except UnidentifiedImageError as e:
                cprint(f"Can't load image '{file}': {e}", "red")

        cprint(f"Saving to {out}", "green")
        pdf.output(str(out))
        add_metadata(out, pdf_metadata, labels, toc)
        # add_labels(out, labels)


def main() -> int:
    parser = argparse.ArgumentParser(prog="pdf.py")
    parser.add_argument("--post", "-p", type=pathlib.Path, help="Path to post to process")
    parser.add_argument("--out", "-o", type=pathlib.Path, help="Path to output directory")

    args = parser.parse_args()

    if args.post is not None:
        content = [Post(args.post)]
    else:
        content = Content()

    outDir = None
    if args.out is not None:
        outDir = args.out

    for post in content:
        if outDir is None:
            od = post.path
        else:
            od = outDir
        out = os.path.join(od, f"{post.path.name}.pdf")
        metadata = post.getMetadata()
        if not "title" in metadata and not "resources" in metadata:
            cprint(f"Skipping post for {out}, since it has no title and resources!", "red")
            continue
        processSingle(post, out)


if __name__ == "__main__":
    sys.exit(main())
