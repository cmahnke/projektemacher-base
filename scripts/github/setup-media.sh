#!/bin/sh
RUN_DEPENDENCIES="ffmpeg"

echo "Installing $RUN_DEPENDENCIES"
sudo apt-get install $RUN_DEPENDENCIES
