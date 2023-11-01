#!/usr/bin/env bash

set -e -o pipefail

( cd fonts && npm --no-audit install )

BASE=fonts
FONT_BASE="$BASE/node_modules"
CSS_DIR="$BASE/out/css"
FONT_DIR="$BASE/out/fonts"

mkdir -p $CSS_DIR $FONT_DIR

for FONT in `find "$FONT_BASE" -type d -depth 2` ;
do
  FONT_NAME=$(basename $FONT)
  echo "Extracting $FONT_NAME from $FONT"
  cat $FONT/*.css >> $CSS_DIR/$FONT_NAME.css
  sed -i '' -E 's/\.\/files/\.\/fonts/g' $CSS_DIR/$FONT_NAME.css
  cp $FONT/files/*.woff* $FONT_DIR
done
cp -n $CSS_DIR/* assets/css/fonts/
cp -n $FONT_DIR/* static/fonts/
