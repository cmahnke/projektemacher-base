#!/bin/sh
RUN_DEPENDENCIES="imagemagick parallel rsync sshpass bash jq findutils libcairo2-dev pkg-config"

echo "Installing $RUN_DEPENDENCIES"
sudo apt-get install $RUN_DEPENDENCIES
