#!/usr/bin/env bash

set -e -o pipefail

RUN_DEPENDENCIES="ffmpeg"

echo "Installing $RUN_DEPENDENCIES"
sudo apt-get install $RUN_DEPENDENCIES
