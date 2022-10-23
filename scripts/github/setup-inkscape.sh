#!/bin/sh

echo "Installing fonts"

BASEDIR=$(dirname "$0")
#sudo cp $BASEDIR/../../static/fonts/*.ttf /usr/local/share/fonts
sudo find $BASEDIR/../../ -iname "static/fonts/*.ttf" -exec cp {} /usr/local/share/fonts \;
fc-cache -f -v
fc-list

echo "Installing Inkscape"

sudo add-apt-repository ppa:inkscape.dev/stable
sudo apt update
sudo apt install inkscape
