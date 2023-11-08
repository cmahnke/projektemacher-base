#!/usr/bin/env bash

IMAGES=$(find . -follow -path '*/out/*.tif' | grep -v cache)
IFS=$'\n'
JOBS=2
JOBFILE=./vips-jobs

>$JOBFILE

for IMAGE in $IMAGES
do
  DIR="$(dirname $IMAGE)/.."
  FILENAME=$(basename $IMAGE .tif)
  echo "Processing '$IMAGE' in '$DIR'"
  mkdir -p "$DIR/jpg/" "$DIR/jxl/"
  # Resample: -set units PixelsPerInch -density 300

  if [ ! -f "$DIR/jpg/$FILENAME.jpg" ] ; then
    convert "$IMAGE" -interlace JPEG -quality 85% "$DIR/jpg/$FILENAME.jpg"
  fi
  if [ ! -f "$DIR/jxl/$FILENAME.jxl" ] ; then
    	echo "Added generation of $DIR/jxl/$FILENAME.jxl to queue"
	#convert "$IMAGE" -define jxl:effort=9 -define jxl:brotli_effort=11 -define jxl:distance=1 "$DIR/jxl/$FILENAME.jxl"
#convert "$IMAGE" -define jxl:quality=90 -define jxl:brotli_effort=11 -define jxl:effort=9 "$DIR/jxl/$FILENAME.jxl"
  #convert "$IMAGE" "$DIR/jxl/$FILENAME.jxl"

    echo " \"$IMAGE\" \"$DIR/jxl/$FILENAME.jxl[distance=1,effort=9]\"" >> $JOBFILE
  fi
done

echo "Running JXL processing with $JOBS jobs, this may take a while"
cat $JOBFILE | xargs -P $JOBS -n 2 vips copy

echo "Number of images: $(echo "$IMAGES"|wc -l|tr -d ' ')"
