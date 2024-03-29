#!/bin/sh

BASEDIR="$(dirname "$0")/../../"
DECOMPRESS_DIR=/tmp/fonts/

docker pull "ghcr.io/cmahnke/font-action:latest"

echo "Installing fonts"

mkdir -p "$DECOMPRESS_DIR"
sudo find $BASEDIR -iname "static/fonts/*.woff2" -print -exec cp {} "$DECOMPRESS_DIR" \;
cd $DECOMPRESS_DIR
for file in "*.woff2" ;
do
  echo "Decompressing $file using Docker"
  docker run -w ${PWD} -v ${PWD}:${PWD} ghcr.io/cmahnke/font-action:latest /usr/local/bin/woff2_decompress "$file" ;
done
sudo find "$DECOMPRESS_DIR" -iname "*.ttf" -print -exec cp {} /usr/local/share/fonts \;
cd $BASEDIR

#sudo cp $BASEDIR/../../static/fonts/*.ttf /usr/local/share/fonts
sudo find $BASEDIR -iname "static/fonts/*.ttf" -print -exec cp {} /usr/local/share/fonts \;
fc-cache -f -v
fc-list

echo "Installing Inkscape"

sudo add-apt-repository ppa:inkscape.dev/stable
sudo apt update
sudo apt install inkscape
