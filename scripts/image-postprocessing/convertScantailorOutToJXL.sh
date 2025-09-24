#!/usr/bin/env bash

IMAGES=$(find . -follow -path '*/out/*.tif' | grep -v cache)
IFS=$'\n'
JOBS=1
JOBFILE=./vips-jobs

EXIF=exiftool

if ! command -v "$EXIF" 2>&1 >/dev/null
then
    echo "exiv2 not found, install it and make sure it's in PATH"
    exit 1
fi

>$JOBFILE

for IMAGE in $IMAGES
do
  DIR="$(dirname $IMAGE)/.."
  FILENAME=$(basename $IMAGE .tif)
  echo "Processing '$IMAGE' in '$DIR'"
  mkdir -p "$DIR/jpg/" "$DIR/jxl/"
  # Resample: -set units PixelsPerInch -density 300

  if [ ! -f "$DIR/jpg/$FILENAME.jpg" ] ; then
    magick "$IMAGE" -interlace JPEG -quality 85% "$DIR/jpg/$FILENAME.jpg"
  fi
  if [ ! -f "$DIR/jxl/$FILENAME.jxl" ] ; then
      #exiv2 can currently only read
      #PPIX=`exiv2 -g Exif.Image.XResolution "$IMAGE" | tr -s ' '  | cut -d ' ' -f 4`
      #PPIY=`exiv2 -g Exif.Image.YResolution "$IMAGE" | tr -s ' '  | cut -d ' ' -f 4`

      PPIX=`$EXIF -XResolution -S -n "$IMAGE" | cut -d ' ' -f 2`
      PPIY=`$EXIF -YResolution -S -n "$IMAGE" | cut -d ' ' -f 2`

    	echo "Added generation of $DIR/jxl/$FILENAME.jxl to queue"

      #
    	#magick "$IMAGE" -define jxl:effort=9 -define jxl:brotli_effort=11 -define jxl:distance=1 "$DIR/jxl/$FILENAME.jxl"
      #magick "$IMAGE" -define jxl:quality=90 -define jxl:brotli_effort=11 -define jxl:effort=9 "$DIR/jxl/$FILENAME.jxl"
      #magick "$IMAGE" "$DIR/jxl/$FILENAME.jxl"

      # exiv2 can currently only read
      #echo "'vips copy \"$IMAGE\" \"$DIR/jxl/$FILENAME.jxl[distance=1,effort=9]\" && $EXIF -M\"set Exif.Image.XResolution Rational $PPIX\" -M\"set Exif.Image.XResolution Rational $PPIY\" \"$DIR/jxl/$FILENAME.jxl\"'" >> $JOBFILE
      echo "'vips copy \"$IMAGE\" \"$DIR/jxl/$FILENAME.jxl[distance=1,effort=9]\" && $EXIF -m \"$DIR/jxl/$FILENAME.jxl\" -resolutionunit=inches -XResolution=$PPIX -YResolution=$PPIY'" >> $JOBFILE
  fi
done

echo "Running JXL processing with $JOBS jobs, this may take a while"
cat $JOBFILE | xargs -P $JOBS -n 1 sh -c

echo "Number of images: $(echo "$IMAGES"|wc -l|tr -d ' ')"

echo "Removing backup files"
find . -follow -path '*/jxl/*.jxl_original' -exec rm {} \;
