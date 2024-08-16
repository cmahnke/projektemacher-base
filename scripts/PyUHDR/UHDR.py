import logging
import tempfile
import atexit

from PIL import Image

from .UHDRApp import UHDRApp
from .Gainmap import save_yuv, pil_to_numpy

class UHDR:
    def __init__(self, image, brightness=None, contrast=None, pipeline=None, debug=False):
        self.uhdrapp = UHDRApp()
        self._image = self._open(image)
        self.brightness = brightness
        self.contrast = contrast
        self.pipeline = pipeline
        self.debug = debug

    def _open(self, file):
        if isinstance(file, str):
            if str(file).endswith('.jxl'):
                if 'jxlpy' not in sys.modules:
                    import jxlpy
                    from jxlpy import JXLImagePlugin
            img = Image.open(file)
            width, height = img.size
        elif isinstance(image, Image.Image):
            img = file
        #Crop if needed
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
                #im = Image.open(temp_input)
            # Convert PIL to opencv
        return img

    def _tmp_img(self):
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".jpg", delete=False, dir=os.getcwd()) as sdr:
            file = sdr.name
            logging.info(f"Saving PIL Image to {file}")
            self._image.save(sdr)
        if not debug:
            atexit.register(os.remove, file)
        else:
            logging.info(f"Debug enabled, keeping file {file} after end of program")
        return file

    @property
    def image(self):
        return self._image

    @property
    def image_cv(self):
        return pil_to_numpy(self._image)

    def process(self, out_file, gainmap = None):
        if gainmap is None:
            yuv_output = tempfile.NamedTemporaryFile(mode="wb")
            if not debug:
                atexit.register(os.remove, yuv_output)
            else:
                logging.info(f"Debug enabled, keeping file {file} after end of program")
            yuv_output = save_yuv(self._image, yuv_output, brightness=self.brightness, contrast=self.contrast, pipeline=self.pipeline)
        else:
            yuv_output = gainmap

        return self.uhdrapp.uhdr_process(self._tmp_img, yuv_output, out_file=out_file)
