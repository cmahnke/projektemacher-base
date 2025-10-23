#!/usr/bin/env bash

set -e

CONTENT_DIR="./content"

FILES=`find $CONTENT_DIR -iname '*.mp4'`
for INPUT in $FILES
do
    OUTPUT_DIR=`dirname $INPUT`
    OUTPUT_FILE=`basename $INPUT mp4`
    OUTPUT="$OUTPUT_DIR/$OUTPUT_FILE"'ogv'
    echo "Converting '$INPUT' to '$OUTPUT'"
    # Needed on Mac OS: https://github.com/homebrew-ffmpeg/homebrew-ffmpeg
    ffmpeg -y -i $INPUT -c:v libtheora -q:v 7 -c:a libvorbis -q:a 4 $OUTPUT
done
