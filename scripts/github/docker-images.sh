#!/usr/bin/env bash

echo "Installing Docker"
sudo apt install docker

# Format ["TAG"]="GLOBAL NAME"
declare -A DOCKER_IMAGES=( ["ghcr.io/cmahnke/iiif-action:latest-jxl-uploader"]="ghcr.io/cmahnke/iiif-action:latest-jxl-uploader"
                           ["ghcr.io/cmahnke/font-action:latest"]="ghcr.io/cmahnke/font-action:latest"
                           ["ghcr.io/cmahnke/jpeg-xl-action/imagemagick:latest"]="ghcr.io/cmahnke/jpeg-xl-action/imagemagick:latest" )

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

echo "The following images are installed:"
docker images
ERR=$?
if [ $ERR -ne 0 ] ; then
  echo "Error $ERR running Docker"
  exit $ERR
fi
