#!/usr/bin/env bash

PDFJS_STATIC_DIR=static/pdfjs
rm -rf $PDFJS_STATIC_DIR

find content/post/ -name info.json -exec dirname {} \; | xargs rm -r
rm -rf docs/* node_modules resources/_gen
rm -rf static/images/favicon*
find content/ -name ogPreview*.svg | xargs rm
find content/ -name ogPreview*.png | xargs rm
find content/ -name ogPreview*.jpg | xargs rm
