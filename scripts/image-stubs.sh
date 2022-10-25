#!/usr/bin/env bash

IMAGES=$(find content -maxdepth 4 -name '*.jxl')
DOCKER_PREFIX="docker run -w ${PWD} -v ${PWD}:${PWD} ghcr.io/cmahnke/iiif-action:latest-jxl-uploader "
OUT_SUFFIX=".jpg"

for IMAGE in $IMAGES
do
    IMAGE_SUFFIX=$(echo $IMAGE |awk -F . '{print $NF}')
    OUTPUT_DIR=`dirname $IMAGE`
    IMAGE_NAME=`basename $IMAGE .$IMAGE_SUFFIX`
    echo "Processing $IMAGE..."
    if [ "$IMAGE_SUFFIX" == "jxl" ] ; then
        OUTPUT_FILE="$OUTPUT_DIR/$IMAGE_NAME$OUT_SUFFIX"
        $DOCKER_PREFIX djxl -j "$IMAGE" "$OUTPUT_FILE"
        echo "Saved $OUTPUT_FILE"
    fi

done
