#!/usr/bin/env bash

# Format ["TAG"]="GLOBAL NAME"
declare -A DOCKER_IMAGES=( ["ghcr.io/cmahnke/iiif-action:latest-jxl-uploader"]="ghcr.io/cmahnke/iiif-action:latest-jxl-uploader" )


for IMAGE in "${!DOCKER_IMAGES[@]}"
do
    if [ "${DOCKER_IMAGES[$IMAGE]}" != "$IMAGE" ] ; then
        echo "Pulling ${DOCKER_IMAGES[$IMAGE]} and tagging as $IMAGE"
        docker pull "${DOCKER_IMAGES[$IMAGE]}"
        docker tag "${DOCKER_IMAGES[$IMAGE]}" "$IMAGE"
    else
        echo "Pulling ${DOCKER_IMAGES[$IMAGE]}"
        docker pull "${DOCKER_IMAGES[$IMAGE]}"
    fi
done
