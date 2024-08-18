#!/usr/bin/env python

import sys, os, io
import argparse
import atexit
import logging
import pathlib
from pathlib import Path

from PIL import Image
import numpy as np
import cv2 as cv
from termcolor import cprint
import ffmpeg

sys.path.append(os.path.dirname(__file__))

from PyUHDR import GainmapPreprocessing, UHDR, get_processors, save_yuv

Image.MAX_IMAGE_PIXELS = 32768 * 32768

default_pipeline = ["grayscale", "denoise", "white_balance", "normalize"]

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def show_write(img, name):
    cv.imwrite(name, img, [cv.IMWRITE_JPEG_QUALITY, 100])
    cv.imshow("grid", img)
    cv.waitKey(0)


def main(argv) -> int:
    global default_pipeline
    actions = get_processors()
    abs_cwd = Path(os.getcwd()).resolve()
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(prog="enhance_image.py")
    parser.add_argument("--input", "-i", action="store", type=pathlib.Path, required=True, help="input image")
    parser.add_argument("--output", "-o", help="output")
    parser.add_argument("--json", "-j", default=None, help="JSON config")
    parser.add_argument("--contrast", "-c", help="contrast 0 to 2, default 1")
    parser.add_argument("--brightness", "-b", help="brightness -1 to 1, default 0")
    parser.add_argument(
        "--pipeline", "-p", nargs="*", choices=[*actions.keys()], help=f"Pipeline arguments, some of {', '.join(actions.keys())}"
    )
    parser.add_argument("--quality", "-q", help="JPEG quality", default=90)

    parser.add_argument("--keep", "-k", default=False, action="store_true", help="keep intermediate files")
    args = parser.parse_args()

    if args.input:
        if args.input.exists():
            infile = str(args.input)
        else:
            print(f"File {str(args.input)} doesn't exist!")
            sys.exit(1)

    abs_input = Path(infile).resolve()
    if abs_cwd not in abs_input.parents:
        logging.warning(f"File {infile} is not in working directory: {os.getcwd()}")
        print("To use docker it's required, that input files are in or below the current working directory!")
        sys.exit(2)

    if args.output:
        output = args.output
    else:
        output = f"{infile}-out.jpg"

    if args.contrast:
        contrast = args.contrast
    else:
        contrast = None

    if args.brightness:
        brightness = args.brightness
    else:
        brightness = None

    if args.quality:
        quality = args.quality

    if args.pipeline is not None:
        if isinstance(args.pipeline, list) and len(args.pipeline) == 0:
            pipeline = None
        else:
            pipeline = args.pipeline
    else:
        pipeline = default_pipeline

    # metadata = {"Exif.Image.XResolution":, "Exif.Image.XResolution": }

    logging.info(f"Quality set to {quality}, contrast to {contrast}, brightness to {brightness}")
    uhdr = UHDR(
        infile, contrast=contrast, brightness=brightness, pipeline=pipeline, debug=args.keep, quality=quality, config=args.json
    )
    uhdr.process(output)


if __name__ == "__main__":
    main(sys.argv[1:])
