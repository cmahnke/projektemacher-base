import os
import sys
import logging
import tempfile
import atexit

from PIL import Image
from PIL.Image import Exif
from PIL.ExifTags import TAGS
import pyexiv2
from .UHDRApp import UHDRApp
from .Gainmap import save_yuv, pil_to_numpy, debug_save
from .UHDRError import UHDRResizeError


class UHDR:
    debug_gainmap = "debug-gainmap.jpg"

    def __init__(self, image, brightness=None, contrast=None, pipeline=None, debug=False, quality=100, metadata=None, scale=True):
        self._uhdrapp = UHDRApp()
        self._image, exif = self._open(image, scale)
        self.brightness = brightness
        self.contrast = contrast
        self.pipeline = pipeline
        self.debug = debug
        if isinstance(metadata, dict):
            self._metadata = metadata
        elif isinstance(metadata, Exif):
            self._metadata = UHDR.convert_exif(metadata)
        if metadata is None:
            self._metadata = exif
        self.quality = quality

    def _open(self, file, scale=True):
        exif = None
        if isinstance(file, str):
            if str(file).endswith(".jxl"):
                if "jxlpy" not in sys.modules:
                    import jxlpy
                    from jxlpy import JXLImagePlugin

                    #pyexiv2.enableBMFF()
            img = Image.open(file)
            pyexiv2.set_log_level(0)
            if not str(file).endswith(".jxl"):
                exif = pyexiv2.Image(file).read_exif()
            else:
                exif = None

        elif isinstance(file, Image.Image):
            img = file
            exif = UHDR.convert_exif(img.getexif())
        elif isinstance(file, (np.ndarray, np.generic)):
            raise ValueError("NumPy array (from OpenCV) as in out not supported")

        # Crop if needed
        w, h = img.size
        logging.debug(f"Loaded image with dimensions {w}x{h}")
        if (w % 2 or h % 2) and scale:

            new_w, new_h = img.size
            new_w -= w % 2
            new_h -= h % 2
            logging.info(f"Resizing image, from {w}x{h} to {new_w}x{new_h}")
            left = (w - new_w) // 2
            top = (h - new_h) // 2

            img = img.crop((left, top, new_w, new_h))

        elif (w % 2 or h % 2) and not scale:
            raise UHDRResizeError("Scaling disabled")
        if w == 0 or h == 0:
            raise UHDRResizeError(f"Scaling from {w}x{h} resulted in width or height of 0")
        return img, exif

    def _tmp_img(self):
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".jpg", delete=False, dir=os.getcwd()) as sdr:
            file = sdr.name
            logging.info(f"Saving PIL Image to {file}")
            self._image.save(sdr, subsampling=0, format="JPEG", quality=self.quality)
        if self._metadata is not None:

            with pyexiv2.Image(file) as img:
                img.modify_exif(self._metadata)
        if not self.debug:
            atexit.register(os.remove, file)
        else:
            logging.info(f"Debug enabled, keeping file {file} after end of program")
        return file

    @property
    def image(self):
        return self._image

    @property
    def uhdrapp(self):
        return self._uhdrapp

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = value

    @property
    def image_cv(self):
        return pil_to_numpy(self._image)

    def process(self, out_file, gainmap=None):
        if gainmap is None:
            tmp_gainmap = tempfile.NamedTemporaryFile(mode="wb", suffix=".yuv", delete=False, dir=os.getcwd())
            yuv_output = tmp_gainmap.name
            logging.info(f"No Gainmap given, generating one to {yuv_output}")
            if not self.debug:
                atexit.register(os.remove, yuv_output)
            else:
                logging.info(f"Debug enabled, keeping file {yuv_output} after end of program")

            yuv_output, gainmap_img = save_yuv(
                self._image,
                yuv_output,
                brightness=self.brightness,
                contrast=self.contrast,
                pipeline=self.pipeline,
            )
            if self.debug:
                debug_save(gainmap_img, UHDR.debug_gainmap)
        else:
            yuv_output = gainmap

        return self._uhdrapp.uhdr_process(self._tmp_img(), yuv_output, out_file=out_file)

    @staticmethod
    def convert_exif(exif):
        pyexiv2_exif = {}
        for tag, value in exif.items():
            pyexiv2_exif[TAGS.get(tag, tag)] = value
        return pyexiv2_exif
