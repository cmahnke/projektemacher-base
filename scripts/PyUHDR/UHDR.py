import logging
import tempfile
import atexit

from .UHDRApp import UHDRApp
from .Gainmap import save_yuv

class UHDR:
    def __init__(self, image, brightness=None, contrast=None):
        self.uhdrapp = UHDRApp()
        self.image = self.open(image)
        self.brightness = brightness
        self.contrast = contrast

    def open(self, file):
        if isinstance(image, str):
            img = Image.open(image)
            width, height = img.size
        elif isinstance(image, Image):
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
        with tempfile.NamedTemporaryFile(mode="wb") as sdr:
            self.image.save(sdr)
            file = sdr.name
        atexit.register(os.remove, file)
        return file

    def process(self, out_file, gainmap = None):
        if gainmap is None:
            yuv_output = tempfile.NamedTemporaryFile(mode="wb")
            atexit.register(os.remove, yuv_output)
            yuv_output = save_yuv(self.image, yuv_output, brightness=self.brightness, contrast=self.contrast)
        else:
            yuv_output = gainmap


        return self.uhdrapp.uhdr_process(self._tmp_img, yuv_output, out_file=out_file)
