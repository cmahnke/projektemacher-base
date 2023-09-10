#!/usr/bin/env bash

TILE_SIZE=512
IIIF_STATIC_CMD=""
OUTPUT_PREFIX=""
DEFAULT_URL_PREFIX="."
IMAGE_PREFIX=content
DOCKER_PREFIX="docker run -w ${PWD} -v ${PWD}:${PWD} ghcr.io/cmahnke/iiif-action:latest-jxl-uploader "
CMD_PREFIX=""
PDF_INFO_CMD="pdfinfo"
PDF_IMAGES_CMD="pdfimages"

if [ -z "$CORES" ] ; then
  # https://stackoverflow.com/a/45181694
  if [ ! command -v getconf &> /dev/null ] ; then
    CORES=2
  else
    CORES=$(getconf _NPROCESSORS_ONLN)
  fi
fi
JOBFILE=$(mktemp -t 3D_JOBS)

if [ -z "$SKIP_IIIF" ] ; then

    if [ -z "$IMAGES" ] ; then
        echo 'No $IMAGES passed - try IMAGES=$(find content -name "*.jpg") ./themes/projektemacher-base/scripts/iiif.sh'
        exit 1
    fi

    if [ -z "$URL_PREFIX" ] ; then
        echo "URL_PREFIX is not set, setting it to '$DEFAULT_URL_PREFIX'"
        URL_PREFIX="$DEFAULT_URL_PREFIX"
    else
        if [ `echo "$URL_PREFIX" | rev| head -c 1` = "/" ] ; then
            URL_PREFIX=`echo $URL_PREFIX |sed 's/.$//'`
            echo "Removed tailing slash: $URL_PREFIX"
        fi
    fi

#    if ! command -v pdfinfo &> /dev/null ; then
#        echo "poppler could not be found, trying vips"
#        PDF_IMAGES_CMD="vips"
#    fi

    if ! command -v vips &> /dev/null ; then
        echo "vips could not be found, using python"
        IIIF_STATIC_CMD="iiif_static.py"
    else
        VIPS_VERSION=`vips -v | cut -d '-' -f 2`
        VIPS_MAJOR=`echo $VIPS_VERSION | cut -d . -f 1`
        VIPS_MINOR=`echo $VIPS_VERSION | cut -d . -f 2`

        if [[ $VIPS_MAJOR -lt 8 && $VIPS_MINOR -lt 10 ]] ; then
            echo "vips is to old, falling back to python"
            IIIF_STATIC_CMD="iiif_static.py"
        else
            IIIF_STATIC_CMD="vips"
        fi

        if ! vips jxlsave &> /dev/null ; then
            echo "vips cant read JPEG XL files, trying docker"
            CMD_PREFIX=$DOCKER_PREFIX
        fi

    fi

    echo "Processing files"

#    # Check for PDF input
#    for IMAGE in $IMAGES
#    do
#        IMAGE_SUFFIX=$(echo $IMAGE |awk -F . '{print $NF}')
#        PDF_DIR=`basename $IMAGE .$IMAGE_SUFFIX`
#        if [ "$IMAGE_SUFFIX" == "pdf" ] ; then
#            $PDF_IMAGES_CMD -tiff $IMAGE $PDF_DIR
#            mv ./$PDF_DIR/* .
#        fi
#    done

    # IIFF
    for IMAGE in $IMAGES
    do

        IMAGE_SUFFIX=$(echo $IMAGE |awk -F . '{print $NF}')
        OUTPUT_DIR=`dirname $IMAGE`
        IIIF_DIR=`basename $IMAGE .$IMAGE_SUFFIX`
        if [ $OUTPUT_PREFIX = ""] ; then
            TARGET=$OUTPUT_DIR/$IIIF_DIR
        else
            TARGET=$OUTPUT_PREFIX/$OUTPUT_DIR/$IIIF_DIR
            mkdir -p $TARGET
        fi
        echo "Processing $IMAGE..."

        if [ "$URL_PREFIX" = "." ] ; then
            IIIF_ID="$URL_PREFIX"
        else
            IIIF_ID="$URL_PREFIX/$(echo $OUTPUT_DIR |cut -d'/' -f2-)"
            echo "Setting IIIF identifier to '$IIIF_ID'"
        fi

        echo "Generating IIIF files for $IMAGE in directory $OUTPUT_DIR, IIIF directory $IIIF_DIR ($TARGET) using '$IIIF_STATIC_CMD'"
        if [ $IIIF_STATIC_CMD = "vips" ] ; then
            FULLDIR=$TARGET/full/full/0/
            mkdir -p $FULLDIR
            if [ "$IMAGE_SUFFIX" == "jxl" ] ; then
                echo "Running Docker for JPEG XL (Prefix '$CMD_PREFIX')"
                $CMD_PREFIX vips dzsave $IMAGE $TARGET -t $TILE_SIZE --layout iiif --id "$IIIF_ID"
                $CMD_PREFIX vips copy $IMAGE $FULLDIR/default.jpg
            else
                vips dzsave $IMAGE $TARGET -t $TILE_SIZE --layout iiif --id "$IIIF_ID"
                cp $IMAGE $FULLDIR/default.jpg
            fi
            if [ -r "$FULLDIR/default.jpg" ] ; then
              echo "Created full image as JPEG at '$FULLDIR/default.jpg'"
            else
              echo "Full reolution JPEG not found at '$FULLDIR/default.jpg'!"
            fi
        elif [ $IIIF_STATIC_CMD = "iiif_static.py" ] ; then
            iiif_static.py -d $TARGET -i "$IIIF_ID" -t $TILE_SIZE $IMAGE
        fi
        if [ -n "$CHOWN_UID" ] ; then
            echo "Changing owner of $TARGET to $CHOWN_UID"
            chown -R $CHOWN_UID $TARGET
        fi

    done

fi
