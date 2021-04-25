#!/usr/bin/env bash

# Format ["TAG"]="GLOBAL NAME"
declare -A DOCKER_IMAGES=( ["ghcr.io/cmahnke/iiif-action:latest"]="ghcr.io/cmahnke/iiif-action:latest-uploader" )


for IMAGE in "${!DOCKER_IMAGES[@]}"
do
    echo "Pulling ${DOCKER_IMAGES[$IMAGE]} and tagging as $IMAGE"
    docker pull "${DOCKER_IMAGES[$IMAGE]}"
    docker tag "${DOCKER_IMAGES[$IMAGE]}" "$IMAGE"
done
