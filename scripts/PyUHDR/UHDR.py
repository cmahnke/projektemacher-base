import os
import logging
import tempfile
import atexit

from PIL import Image
import pyexiv2
from .UHDRApp import UHDRApp
from .Gainmap import save_yuv, pil_to_numpy


class UHDR:
    def __init__(
        self,
        image,
        brightness=None,
        contrast=None,
        pipeline=None,
        debug=False,
        quality=100,
        metadata=None,
    ):
        self._uhdrapp = UHDRApp()
        self._image, exif = self._open(image)
        self.brightness = brightness
        self.contrast = contrast
        self.pipeline = pipeline
        self.debug = debug
        self._metadata = metadata
        if self._metadata is None:
            self._metadata = exif
        self.quality = quality

    def _open(self, file):
        exif = None
        if isinstance(file, str):
            if str(file).endswith(".jxl"):
                if "jxlpy" not in sys.modules:
                    import jxlpy
                    from jxlpy import JXLImagePlugin
            img = Image.open(file)
            width, height = img.size
            exif = pyexiv2.Image(file).read_exif()

        elif isinstance(image, Image.Image):
            img = file
            exif = img.getexif()
            # TODO: convert to pyexiv2 structure
            raise

        # Crop if needed
        w, h = img.size
        if w % 2 or h % 2:
            logging.info(f"Resizing iamge, size {w}x{h}")
            new_w, new_h = im.size
            new_w -= w % 2
            new_h -= h % 2
            img = img.crop((0, 0, new_w, new_h))
        #            if w != new_w or h != new_h:
        #                temp_input = f"{input}-tmp.jpg"
        #                logging.info(f"Input image reszized to {temp_input}, size {new_w}x{new_h}")
        #                if not args.keep:
        #                    atexit.register(os.remove, temp_input)
        #                im.save(temp_input)
        #                input = temp_input
        # im = Image.open(temp_input)
        # Convert PIL to opencv
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
            yuv_output = tempfile.NamedTemporaryFile(mode="wb")
            if not self.debug:
                atexit.register(os.remove, yuv_output)
            else:
                logging.info(f"Debug enabled, keeping file {yuv_output} after end of program")
            yuv_output = save_yuv(
                self._image,
                yuv_output,
                brightness=self.brightness,
                contrast=self.contrast,
                pipeline=self.pipeline,
            )
        else:
            yuv_output = gainmap

        return self._uhdrapp.uhdr_process(self._tmp_img(), yuv_output, out_file=out_file)
