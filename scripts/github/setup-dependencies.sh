#!/bin/sh
RUN_DEPENDENCIES="bash imagemagick parallel rsync sshpass bash jq findutils libcairo2-dev pkg-config ffmpeg vips"

echo "Installing $RUN_DEPENDENCIES"
sudo apt-get install $RUN_DEPENDENCIES
