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
. $SCRIPT_DIR/node/dependency-management.sh

BASE=$THEME_PATH/fonts
FONT_BASE="$BASE/node_modules"
CSS_DIR="$BASE/out/css"
SCSS_DIR="$BASE/out/scss"
FONT_DIR="$BASE/out/fonts"
SITE_CSS=assets/css/fonts/
SITE_SCSS=assets/scss/npm-fonts/
SITE_FONTS=static/fonts/
PACKAGE_JSON=package.json

echo "Installing Fonts to $BASE"

if [ "$DEPENDENCY_MANAGER" = 'npm' ] ; then
  INSTALL_OPTS="--omit=dev"
fi

if [ "$DEPENDENCY_MANAGER" = 'pnpm' ] ; then
  rm -rf $BASE/node_modules
  INSTALL_OPTS="-P"
fi
if [ "$DEPENDENCY_MANAGER" = 'yarn' ] ; then
  INSTALL_OPTS="--prod"
fi

( cd $BASE && $DEPENDENCY_MANAGER $MANAGER_OPTS install $INSTALL_OPTS )

mkdir -p $CSS_DIR $SCSS_DIR $FONT_DIR $SITE_CSS $SITE_SCSS $SITE_FONTS

DEFINITION=$BASE/$PACKAGE_JSON

for FONT in `find "$FONT_BASE" -mindepth 2 -maxdepth 2 -not -path '*/.*' \( -type l -o -type d \)` ;
do
  FONT_NAME=$(basename $FONT)
  PACKAGE_SOURCE=$(grep "$FONT_NAME" $DEFINITION)
  #if [ "$PACKAGE_SOURCE" == *"variable"* ] ; then
  if grep -q "variable" <<< "$PACKAGE_SOURCE"; then
    echo "Font is variable"
    ALIAS="-variable"
  fi
  echo "Extracting $FONT_NAME from $FONT"
  cat $FONT/*.css >> $CSS_DIR/$FONT_NAME.css
  $SED -i -E 's/\.\/files/\/fonts/g' $CSS_DIR/$FONT_NAME.css
  if [ -n "$ALIAS" ] ; then
    echo "Creating copy of $FONT_NAME as $CSS_DIR/$FONT_NAME$ALIAS.css"
    cp "$CSS_DIR/$FONT_NAME.css" "$CSS_DIR/$FONT_NAME$ALIAS.css"
  fi
  echo "Creating experimental SCSS variant"
  cat $FONT/*.css >> $SCSS_DIR/$FONT_NAME.scss
  $SED -i -E 's/\.\/files/#{$font-base-path}fonts/g' $SCSS_DIR/$FONT_NAME.scss
  $SED -i '1s;^;$font-base-path: \"/\" !default\;\n;' $SCSS_DIR/$FONT_NAME.scss
  if [ -n "$ALIAS" ] ; then
    echo "Creating copy of $FONT_NAME as $SCSS_DIR/$FONT_NAME$ALIAS.scss"
    cp "$SCSS_DIR/$FONT_NAME.scss" "$SCSS_DIR/$FONT_NAME$ALIAS.scss"
  fi
  cp $FONT/files/*.woff* $FONT_DIR
done
rm -f fonts/out/css/@*
echo "Copying CSS to '$SITE_CSS'"
cp -n $CSS_DIR/* $SITE_CSS ||/usr/bin/true
cp -n $SCSS_DIR/* $SITE_SCSS ||/usr/bin/true
echo "Copying Fonts to '$SITE_FONTS'"
cp -n $FONT_DIR/* $SITE_FONTS ||/usr/bin/true
