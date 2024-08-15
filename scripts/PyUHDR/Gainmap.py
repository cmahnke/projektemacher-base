import logging
import cv2 as cv
import numpy as np
import ffmpeg
from PIL import Image

def save_yuv(img, output_file, brightness=None, contrast=None):
    if isinstance(img, (np.ndarray, np.generic)):
        pass
    elif isinstance(image, Image):
        img = cv.cvtColor(np.array(img.convert('RGB')), cv.COLOR_RGB2BGR)

    if len(img.shape) < 3:
        img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    height, width, channels = img.shape

    #args = ['ffmpeg', '-i', 'pipe:', '-filter:v', 'format=p010', name]
    #cprint(f"$ {' '.join(args)}", 'yellow')

    if brightness is not None or contrast is not None:
        eq = {}
        if brightness is not None :
            eq["brightness"] = brightness
        if contrast is not None:
            eq["contrast"] = contrast

        logging.info(f"Equalizer settings to be used {eq}")
        converter = (
            ffmpeg.input('pipe:', format='rawvideo', pix_fmt='bgr24', s=f"{width}x{height}").filter("eq", **eq)
            .filter("format", "p010").output(output_file).overwrite_output().run_async(pipe_stdin=True)
        )
    else:

        converter = (
            ffmpeg.input('pipe:', format='rawvideo', pix_fmt='bgr24', s=f"{width}x{height}")
            .filter("format", "p010").output(output_file).overwrite_output().run_async(pipe_stdin=True)
        )
    converter.communicate(input=img.astype(np.uint8).tobytes())
    converter.stdin.close()
    converter.wait()
    return output_file
