import logging
from pathlib import Path

import pyvips

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".jxl": "jxl", ".jpg": "jpeg", ".jpeg": "jpeg", ".tif": "tiff", ".tiff": "tiff", ".png": "png"}

# libvips reports resolution in pixels per millimeter and defaults to 1.0 when
# metadata is missing (see scripts/pdf.py); 2.0 px/mm would be ~51 dpi, real
# scans are denser than that.
MIN_MEANINGFUL_PX_PER_MM = 2.0


def is_image(path) -> bool:
    return Path(path).suffix.lower() in IMAGE_EXTENSIONS


def image_format(path) -> str:
    return IMAGE_EXTENSIONS[Path(path).suffix.lower()]


def load(path) -> pyvips.Image:
    return pyvips.Image.new_from_file(str(path), access="random")


def dpi(image: pyvips.Image) -> int:
    try:
        xres = image.get("xres")
    except Exception:
        return None
    if xres is None or xres <= MIN_MEANINGFUL_PX_PER_MM:
        return None
    return round(xres * 25.4)


def to_image_bytes(image: pyvips.Image, max_side=4000, fmt="jpeg", quality=92) -> bytes:
    if max(image.width, image.height) > max_side:
        image = image.thumbnail_image(max_side)
    if image.hasalpha():
        fmt = "png"
    if fmt == "png":
        return image.write_to_buffer(".png")
    return image.write_to_buffer(".jpg", Q=quality)
