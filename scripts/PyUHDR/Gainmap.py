import logging
from inspect import getmembers, isfunction

import cv2 as cv
import numpy as np
import ffmpeg
from PIL import Image


class GainmapPreprocessing:
    def normalize(img):
        # cvAr = greyscale(pilImg)
        norm = cv.normalize(src=img, dst=None, beta=0, alpha=255, norm_type=cv.NORM_MINMAX)
        return norm

    def grayscale(img):
        return cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    def denoise(img):
        return cv.fastNlMeansDenoising(img)

    def smoothen(img):
        return cv.bilateralFilter(cvAr, 25, 75, 75)

    def white_balance(img, balancer="simple"):
        if balancer == "simple":
            wb = cv.xphoto.createSimpleWB()
        elif balencer == "grayworld":
            wb = cv.xphoto.createGrayworldWB()
        return wb.balanceWhite(img)

    def invert(img):
        return cv.bitwise_not(img)


def get_processors():
    processors = {}
    for function in getmembers(GainmapPreprocessing, predicate=isfunction):
        processors[function[0]] = function[1]
    return processors


def process(img, pipeline):
    if isinstance(img, Image.Image):
        img = pil_to_numpy(img)
    logging.info(f"Processing pipline {', '.join(pipeline)}")
    for processor in pipeline:
        logging.info(f"Running processor {processor}")
        img = processors[processor](img)
    return img


def save_yuv(
    img,
    output_file,
    brightness=None,
    contrast=None,
    pipeline=None,
):
    if isinstance(img, (np.ndarray, np.generic)):
        pass
    elif isinstance(img, Image.Image):
        img = pil_to_numpy(img)

    if pipeline is not None and len(pipeline):
        img = process(img, pipeline)

    if len(img.shape) < 3:
        img = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    height, width, channels = img.shape

    if brightness is not None or contrast is not None:
        eq = {}
        if brightness is not None:
            eq["brightness"] = brightness
        if contrast is not None:
            eq["contrast"] = contrast

        logging.info(f"Equalizer settings to be used {eq}")
        converter = (
            ffmpeg.input("pipe:", format="rawvideo", pix_fmt="bgr24", s=f"{width}x{height}")
            .filter("eq", **eq)
            .filter("format", "p010")
            .output(output_file)
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )
    else:
        converter = (
            ffmpeg.input("pipe:", format="rawvideo", pix_fmt="bgr24", s=f"{width}x{height}")
            .filter("format", "p010")
            .output(output_file)
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )
    converter.communicate(input=img.astype(np.uint8).tobytes())
    converter.stdin.close()
    converter.wait()

    return (output_file, img)


def pil_to_numpy(img):
    return cv.cvtColor(np.array(img.convert("RGB")), cv.COLOR_RGB2BGR)


def debug_save(img, file):
    if isinstance(img, Image.Image):
        img.save(file)
    elif isinstance(img, (np.ndarray, np.generic)):
        cv.imwrite(file, img, [cv.IMWRITE_JPEG_QUALITY, 100])


processors = get_processors()
