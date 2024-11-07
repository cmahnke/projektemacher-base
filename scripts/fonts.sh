#!/usr/bin/env bash

set -e -o pipefail

SED=sed
REALPATH=realpath
OS="`uname`"
case "$OS" in
  'Darwin')
    SED=gsed
    REALPATH=grealpath
    ;;
  'Linux')
    SED=sed
    REALPATH=realpath
    ;;
esac

if [ -n "$1" ] ; then
  THEME_PATH="$1"
fi

if [ -z "$THEME_PATH" ] ; then
  THEME_PATH=.
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
$SCRIPT_DIR/node/dependency-management.sh

BASE=$THEME_PATH/fonts
FONT_BASE="$BASE/node_modules"
CSS_DIR="$BASE/out/css"
FONT_DIR="$BASE/out/fonts"
SITE_CSS=assets/css/fonts/
SITE_FONTS=static/fonts/

echo "Installing Fonts to $BASE"

if [ "$DEPENDENCY_MANAGER" = 'npm' ] ; then
  INSTALL_OPTS="--omit=dev"
fi

if [ "$DEPENDENCY_MANAGER" = 'pnpm' ] ; then
  INSTALL_OPTS="-P"
fi

( cd $BASE && $DEPENDENCY_MANAGER $MANAGER_OPTS install $INSTALL_OPTS )

mkdir -p $CSS_DIR $FONT_DIR $SITE_CSS $SITE_FONTS

for FONT in `find "$FONT_BASE" -mindepth 2 -maxdepth 2 -type d` ;
do
  FONT_NAME=$(basename $FONT)
  echo "Extracting $FONT_NAME from $FONT"
  cat $FONT/*.css >> $CSS_DIR/$FONT_NAME.css
  $SED -i -E 's/\.\/files/\/fonts/g' $CSS_DIR/$FONT_NAME.css
  cp $FONT/files/*.woff* $FONT_DIR
done
echo "Copying CSS to '$SITE_CSS'"
cp -n $CSS_DIR/* $SITE_CSS ||/usr/bin/true
echo "Copying Fonts to '$SITE_FONTS'"
cp -n $FONT_DIR/* $SITE_FONTS ||/usr/bin/true
