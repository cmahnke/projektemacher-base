#!/bin/sh
RUN_DEPENDENCIES="bash coreutils imagemagick parallel rsync sshpass bash jq findutils libcairo2-dev pkg-config poppler-utils	libvips-tools moby-cli patchelf wget"
DOCKER_DEPENDENCIES="docker-buildx-plugin docker-ce docker-ce-cli"

echo "Installing $RUN_DEPENDENCIES $DOCKER_DEPENDENCIES"
sudo apt-get update
sudo apt-get install $RUN_DEPENDENCIES $DOCKER_DEPENDENCIES
