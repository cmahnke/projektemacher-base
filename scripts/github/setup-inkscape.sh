#!/bin/sh

echo "Installing Inkscape"

sudo add-apt-repository ppa:inkscape.dev/stable
sudo apt update
sudo apt install inkscape

echo "Installing fonts"

BASEDIR=$(dirname "$0")
sudo cp $BASEDIR/../static/fonts/*.ttf /usr/local/share/fonts
fc-cache -f -v
