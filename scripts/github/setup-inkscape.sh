#!/bin/sh

BASEDIR="$(dirname "$0")/../../"

$BASEDIR/scripts/github/setup-system-fonts.sh

echo "Installing Inkscape"

sudo add-apt-repository ppa:inkscape.dev/stable
sudo apt update
sudo apt install inkscape ghostscript
