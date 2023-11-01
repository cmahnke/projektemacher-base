#!/usr/bin/env bash

set -e -o pipefail

if [ -z "$THEME_PATH" ] ; then
  THEME_PATH=.
fi

BASE=$THEME_PATH/fonts
FONT_BASE="$BASE/node_modules"
CSS_DIR="$BASE/out/css"
FONT_DIR="$BASE/out/fonts"
SITE_CSS=assets/css/fonts/
SITE_FONTS=static/fonts/

( cd $BASE && npm --no-audit install )

mkdir -p $CSS_DIR $FONT_DIR $SITE_CSS $SITE_FONTS

for FONT in `find "$FONT_BASE" -maxdepth 2 -type d` ;
do
  FONT_NAME=$(basename $FONT)
  echo "Extracting $FONT_NAME from $FONT"
  cat $FONT/*.css >> $CSS_DIR/$FONT_NAME.css
  sed -i '' -E 's/\.\/files/\.\/fonts/g' $CSS_DIR/$FONT_NAME.css
  cp $FONT/files/*.woff* $FONT_DIR
done
echo "Copying CSS"
cp -n $CSS_DIR/* $SITE_CSS ||/usr/bin/true
echo "Copying Fonts"
cp -n $FONT_DIR/* $SITE_FONTS
