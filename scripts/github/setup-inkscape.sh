#!/bin/sh

DECOMPRESS_DIR=/tmp/fonts/

docker pull "ghcr.io/cmahnke/font-action:latest"

echo "Installing fonts"

mkdir -p "$DECOMPRESS_DIR"
sudo find $BASEDIR/../../ -iname "static/fonts/*.woff2" -exec cp {} "$DECOMPRESS_DIR" \;
for file in "$DECOMPRESS_DIR/*.woff2" ;
do
  docker run -w ${PWD} -v ${PWD}:${PWD} ghcr.io/cmahnke/font-action:latest /usr/local/bin/woff2_decompress "$file" ;
done
sudo find "$DECOMPRESS_DIR" -iname "*.ttf" -exec cp {} /usr/local/share/fonts \;


BASEDIR=$(dirname "$0")
#sudo cp $BASEDIR/../../static/fonts/*.ttf /usr/local/share/fonts
sudo find $BASEDIR/../../ -iname "static/fonts/*.ttf" -exec cp {} /usr/local/share/fonts \;
fc-cache -f -v
fc-list

echo "Installing Inkscape"

sudo add-apt-repository ppa:inkscape.dev/stable
sudo apt update
sudo apt install inkscape
