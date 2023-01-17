#!/bin/sh
RUN_DEPENDENCIES="bash coreutils imagemagick parallel rsync sshpass bash jq findutils libcairo2-dev pkg-config poppler-utils	libvips-tools moby-cli patchelf wget"

echo "Installing $RUN_DEPENDENCIES"
sudo apt-get install $RUN_DEPENDENCIES
