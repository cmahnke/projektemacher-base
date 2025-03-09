#!/usr/bin/env bash

# Favicons
echo "Generating favicons from $SOURCE"

# See https://gist.github.com/pfig/1808188
case "$SOURCE" in
  *.svg)
    CMD="convert -background none -density 2400 \"$SOURCE\" $OPTIONS static/images/favicon.png" ;;
  *)
    CMD="convert \"$SOURCE\" $OPTIONS static/images/favicon.png" ;;
esac


eval $CMD
#
convert static/images/favicon.png -resize 512x512 static/images/favicon-512.png
convert static/images/favicon.png -resize 256x256 static/images/favicon-256.png
convert static/images/favicon-256.png -resize 128x128 -transparent white static/images/favicon-128.png
convert static/images/favicon-256.png -resize 64x64 -transparent white static/images/favicon-64.png
convert static/images/favicon-256.png -resize 32x32 -transparent white static/images/favicon-32.png

convert static/images/favicon-32.png static/images/favicon-64.png static/images/favicon-128.png -colors 256 static/images/favicon.ico

convert static/images/favicon.png -resize 128x128 static/images/favicon-128.png
convert static/images/favicon.png -resize 64x64 static/images/favicon-64.png
convert static/images/favicon.png -resize 32x32 static/images/favicon-32.png
convert static/images/favicon.png -resize 180x180 static/images/apple-touch-icon.png
