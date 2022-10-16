#!/usr/bin/env bash

CONTENT_DIR="./content"

FILES=`find $CONTENT_DIR -iname '*.mp4'`
for INPUT in $FILES
do
    OUTPUT_DIR=`dirname $INPUT`
    OUTPUT_FILE=`basename $INPUT mp4`
    OUTPUT="$OUTPUT_DIR/$OUTPUT_FILE"'ogv'
    echo "Converting '$INPUT' to '$OUTPUT'"
    ffmpeg -i $INPUT -c: v libtheora -q: v 10 -c: a libvorbis -q: a 10 $OUTPUT
done
