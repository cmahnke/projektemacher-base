#!/usr/bin/env bash
DEFAULT_SOURCE=content
DEFAULT_FILENAME="ogPreview*.svg"
DEFAULT_BACKGROUND=white
DEFAULT_TARGETFORMAT=jpg

IMAGEMAGIC="convert"
#IMAGEMAGIC="magick"

if [ -z "$SOURCE" ] ; then
    SOURCE=$DEFAULT_SOURCE
fi
if [ -z "$FILENAME" ] ; then
    FILENAME=$DEFAULT_FILENAME
fi

if [ -z "$BACKGROUND" ] ; then
    BACKGROUND=$DEFAULT_BACKGROUND
fi

if [ -z "$TARGETFORMAT" ] ; then
    TARGETFORMAT=$DEFAULT_TARGETFORMAT
fi

BASEDIR=$(dirname "$0")

echo "Generating previews for $FILENAME from $SOURCE - background $BACKGROUND"

# Generate Previews
python3 $BASEDIR/preview.py

if [ $TARGETFORMAT != "png" ] ; then
    find $SOURCE -name "$FILENAME" -print -exec bash -c 'inkscape "{}" --export-filename=$(dirname "{}")/$(basename -s .svg "{}").png; '$IMAGEMAGIC' $(dirname "{}")/$(basename -s .svg "{}").png -background '$BACKGROUND' -flatten $(dirname "{}")/$(basename -s .svg "{}").'$TARGETFORMAT'; rm "{}"' \;
else
    find $SOURCE -name "$FILENAME" -print -exec bash -c 'inkscape "{}" --export-filename=$(dirname "{}")/$(basename -s .svg "{}").png' \;
fi

#; rm $(dirname "{}")/$(basename -s .svg "{}").png
