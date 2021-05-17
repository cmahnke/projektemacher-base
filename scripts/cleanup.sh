#!/usr/bin/env bash

find content/post/ -name info.json -exec dirname {} \; | xargs rm -r
rm -rf docs/* node_modules resources/_gen
rm -rf static/images/favicon*
find content/ -name ogPreview*.svg | xargs rm
find content/ -name ogPreview*.png | xargs rm
find content/ -name ogPreview*.jpg | xargs rm
