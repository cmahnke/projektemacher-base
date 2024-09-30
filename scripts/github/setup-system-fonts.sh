#!/usr/bin/env bash

BASEDIR="$(pwd)/$(dirname "$0")/../../"
DECOMPRESS_DIR=./tmp/fonts/
FONT_LIST=../fonts.lst
JOBS=`nproc --all`

docker pull "ghcr.io/cmahnke/font-action:latest"

echo "Installing fonts"

mkdir -p "$DECOMPRESS_DIR"
find $BASEDIR -path "*static/fonts/*.woff2" -print -exec cp {} "$DECOMPRESS_DIR" \;
cd $DECOMPRESS_DIR
for file in `ls *.woff2` ;
do
  echo "Decompressing font $file using Docker"
  echo $file >> $FONT_LIST
  #docker run -w ${PWD} -v ${PWD}:${PWD} ghcr.io/cmahnke/font-action:latest /usr/local/bin/woff2_decompress "$file" ;
done
cat $FONT_LIST | xargs -P $JOBS -n 1 docker run -w ${PWD} -v ${PWD}:${PWD} ghcr.io/cmahnke/font-action:latest /usr/local/bin/woff2_decompress
cd $BASEDIR

SYSTEM_FONT_DIR=/usr/local/share/fonts
OS="`uname`"
case "$OS" in
  'Darwin')
    echo "The following files would be copied to $SYSTEM_FONT_DIR"
    find "$DECOMPRESS_DIR" -name "*.ttf" -print
    find $BASEDIR -path "*static/fonts/*.ttf" -print
    ;;
  'Linux')
    sudo find "$DECOMPRESS_DIR" -name "*.ttf" -print -exec cp {} $SYSTEM_FONT_DIR \;
    sudo find $BASEDIR -path "*static/fonts/*.ttf" -print -exec cp {} $SYSTEM_FONT_DIR \;
    fc-cache -f -v
    fc-list
    ;;
esac



#rm -rf $DECOMPRESS_DIR

#sudo cp $BASEDIR/../../static/fonts/*.ttf /usr/local/share/fonts
