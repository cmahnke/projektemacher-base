#!/usr/bin/env bash

set -e -o pipefail

DOCKER_IMAGE="ghcr.io/cmahnke/font-action:latest"

if [ -n "$1" ] ; then
  BASEDIR="$1"
else
  BASEDIR="$(dirname "$0")/../../"
  #BASEDIR="$(readlink -f "$0")/../../"
fi

if [[ ${var:0:1} != / ]] ; then
  BASEDIR=`realpath $BASEDIR`
fi

echo "BASEDIR is set to $BASEDIR"

DECOMPRESS_DIR=./tmp/fonts/
FONT_LIST=../fonts.lst
JOBS=`nproc --all`

echo "Installing fonts"

mkdir -p "$DECOMPRESS_DIR"
find $BASEDIR -path "*static/fonts/*.woff2" -print -exec cp {} "$DECOMPRESS_DIR" \;
cd $DECOMPRESS_DIR
DECOMPRESS_DIR=`pwd`
for file in `ls *.woff2` ;
do
  echo "Decompressing font $file using Docker"
  echo $file >> $FONT_LIST
  #docker run -w ${PWD} -v ${PWD}:${PWD} ghcr.io/cmahnke/font-action:latest /usr/local/bin/woff2_decompress "$file" ;
done

if [ -z "$FONT_CONVERT_CMD" ] ; then
  docker pull "$DOCKER_IMAGE"
  FONT_CONVERT_CMD="docker run -w ${PWD} -v ${PWD}:${PWD} $DOCKER_IMAGE /usr/local/bin/woff2_decompress"
fi

cat $FONT_LIST | xargs -P $JOBS -n 1 $FONT_CONVERT_CMD

echo "Created files (in $DECOMPRESS_DIR):"
find . -name "*.ttf" -print

cd $BASEDIR

SYSTEM_FONT_DIR=/usr/local/share/fonts
OS="`uname`"
case "$OS" in
  'Darwin')
    echo "The following files have been copied to $SYSTEM_FONT_DIR"
    find "$DECOMPRESS_DIR" -name "*.ttf" -print
    find $BASEDIR -path "*static/fonts/*.ttf" -print
    ;;
  'Linux')
    echo "The following files have been copied to $SYSTEM_FONT_DIR"
    sudo find "$DECOMPRESS_DIR" -name "*.ttf" -print -exec cp {} $SYSTEM_FONT_DIR \;
    sudo find $BASEDIR -path "*static/fonts/*.ttf" -print -exec cp {} $SYSTEM_FONT_DIR \;
    fc-cache -f -v
    fc-list
    ;;
esac



#rm -rf $DECOMPRESS_DIR

#sudo cp $BASEDIR/../../static/fonts/*.ttf /usr/local/share/fonts
