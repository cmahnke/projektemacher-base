#!/usr/bin/env bash
DEFAULT_SOURCE=content
DEFAULT_FILENAME="ogPreview*.svg"
DEFAULT_BACKGROUND=white

if [ -z "$SOURCE" ] ; then
    SOURCE=$DEFAULT_SOURCE
fi
if [ -z "$FILENAME" ] ; then
    FILENAME=$DEFAULT_FILENAME
fi

if [ -z "$BACKGROUND" ] ; then
    BACKGROUND=$DEFAULT_BACKGROUND
fi

BASEDIR=$(dirname "$0")

echo "Generating previews for $FILENAME from $SOURCE - background $BACKGROUND"

# Generate Previews
python3 $BASEDIR/preview.py


find $SOURCE -name "$FILENAME" -print -exec bash -c 'inkscape "{}" --export-filename=$(dirname "{}")/$(basename -s .svg "{}").png; convert $(dirname "{}")/$(basename -s .svg "{}").png -background '$BACKGROUND' -flatten $(dirname "{}")/$(basename -s .svg "{}").jpg; rm "{}"' \;

#; rm $(dirname "{}")/$(basename -s .svg "{}").png
