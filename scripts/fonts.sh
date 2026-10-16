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
  PACKAGE_SOURCE=$(grep -E "\"@fontsource(-variable)?/$FONT_NAME\":" $DEFINITION)
  #if [ "$PACKAGE_SOURCE" == *"variable"* ] ; then
  if grep -q "variable" <<< "$PACKAGE_SOURCE"; then
    echo "Font is variable"
    ALIAS="-variable"
  else
    echo "Font is not variable"
    ALIAS=""
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
  $SED -i '$!N; /^\(.*\)\n\1$/!P; D' $SCSS_DIR/$FONT_NAME.scss
  if [ -n "$ALIAS" ] ; then
    echo "Creating copy of $FONT_NAME as $SCSS_DIR/$FONT_NAME$ALIAS.scss"
    cp "$SCSS_DIR/$FONT_NAME.scss" "$SCSS_DIR/$FONT_NAME$ALIAS.scss"
  fi
  cp $FONT/files/*.woff* $FONT_DIR
done
rm -f "$CSS_DIR"/@*

# Compatibility copies: create the legacy file names (used before the fonts were
# provided by the Fontsource npm packages) from the npm files, so existing
# @font-face rules referencing '/fonts/<legacy name>' keep working without the
# fonts being tracked in the repository.
# Sources are looked up in $FONT_DIR; missing sources are skipped with a warning.
copy_legacy_font() {
  if [ ! -f "$SITE_FONTS/$1" ] ; then
    if [ -f "$FONT_DIR/$2" ] ; then
      cp "$FONT_DIR/$2" "$SITE_FONTS/$1"
      echo "Legacy font copy: $2 -> $1"
    else
      echo "Warning: no npm file found for legacy font name '$1' (expected '$FONT_DIR/$2')"
    fi
  fi
}

# berkshire-swash (static)
for EXT in woff woff2 ; do
  copy_legacy_font "berkshire-swash-v9-latin-regular.$EXT" "berkshire-swash-latin-400-normal.$EXT"
done

# cormorant (static)
for PAIR in "regular 400-normal" "italic 400-italic" "700 700-normal" "700italic 700-italic" ; do
  LEGACY=$(echo $PAIR | cut -d ' ' -f 1)
  CURRENT=$(echo $PAIR | cut -d ' ' -f 2)
  for EXT in woff woff2 ; do
    copy_legacy_font "cormorant-v10-latin-$LEGACY.$EXT" "cormorant-latin-$CURRENT.$EXT"
  done
done

# courier-prime (static)
for PAIR in "regular 400-normal" "italic 400-italic" "700 700-normal" "700italic 700-italic" ; do
  LEGACY=$(echo $PAIR | cut -d ' ' -f 1)
  CURRENT=$(echo $PAIR | cut -d ' ' -f 2)
  for EXT in woff woff2 ; do
    copy_legacy_font "courier-prime-v7-latin-$LEGACY.$EXT" "courier-prime-latin-$CURRENT.$EXT"
  done
done

# eb-garamond (variable, woff2 only)
for WEIGHT in 500 600 700 800 regular ; do
  copy_legacy_font "eb-garamond-v15-latin-$WEIGHT.woff2" "eb-garamond-latin-wght-normal.woff2"
done
for WEIGHT in 500italic 600italic 700italic 800italic italic ; do
  copy_legacy_font "eb-garamond-v15-latin-$WEIGHT.woff2" "eb-garamond-latin-wght-italic.woff2"
done

# inconsolata (variable, woff2 only)
for WEIGHT in 400 700 900 ; do
  copy_legacy_font "Inconsolata_${WEIGHT}_normal.woff2" "inconsolata-latin-wght-normal.woff2"
done

# josefin-sans (variable, woff2 only)
for STYLE in Thin ExtraLight Light Regular Medium SemiBold Bold Italic ; do
  copy_legacy_font "JosefinSans-$STYLE.woff2" "josefin-sans-latin-wght-normal.woff2"
done
for STYLE in ThinItalic ExtraLightItalic LightItalic MediumItalic SemiBoldItalic BoldItalic ; do
  copy_legacy_font "JosefinSans-$STYLE.woff2" "josefin-sans-latin-wght-italic.woff2"
done

# lato (static)
for PAIR in "regular 400" "700 700" ; do
  LEGACY=$(echo $PAIR | cut -d ' ' -f 1)
  WEIGHT=$(echo $PAIR | cut -d ' ' -f 2)
  for EXT in woff woff2 ; do
    copy_legacy_font "lato-v17-latin-$LEGACY.$EXT" "lato-latin-$WEIGHT-normal.$EXT"
  done
done

# league-spartan (variable, woff2 only)
for STYLE in ExtraLight Light Regular Medium SemiBold Bold ; do
  copy_legacy_font "LeagueSpartan-$STYLE.woff2" "league-spartan-latin-wght-normal.woff2"
done

# libre-baskerville (static)
for PAIR in "regular 400-normal" "italic 400-italic" ; do
  LEGACY=$(echo $PAIR | cut -d ' ' -f 1)
  CURRENT=$(echo $PAIR | cut -d ' ' -f 2)
  for EXT in woff woff2 ; do
    copy_legacy_font "libre-baskerville-v9-latin-ext_latin-$LEGACY.$EXT" "libre-baskerville-latin-$CURRENT.$EXT"
  done
done

# lora (variable, woff2 only)
for WEIGHT in regular 700 ; do
  copy_legacy_font "lora-v16-latin-$WEIGHT.woff2" "lora-latin-wght-normal.woff2"
done

# montserrat (variable, woff2 only)
for WEIGHT in 200 300 regular 500 600 700 800 ; do
  copy_legacy_font "montserrat-v15-latin-$WEIGHT.woff2" "montserrat-latin-wght-normal.woff2"
done
for WEIGHT in 200italic 300italic italic 500italic 600italic 700italic ; do
  copy_legacy_font "montserrat-v15-latin-$WEIGHT.woff2" "montserrat-latin-wght-italic.woff2"
done
for WEIGHT in regular 500 ; do
  copy_legacy_font "montserrat-v25-latin-ext-$WEIGHT.woff2" "montserrat-latin-ext-wght-normal.woff2"
done
copy_legacy_font "montserrat-v25-latin-ext-500italic.woff2" "montserrat-latin-ext-wght-italic.woff2"

# noto-serif-display (variable, woff2 only)
for SUBSET in latin latin-ext ; do
  for WEIGHT in 100 200 300 400 500 600 700 800 900 ; do
    copy_legacy_font "noto-serif-display-$SUBSET-$WEIGHT-normal.woff2" "noto-serif-display-$SUBSET-wght-normal.woff2"
    copy_legacy_font "noto-serif-display-$SUBSET-$WEIGHT-italic.woff2" "noto-serif-display-$SUBSET-wght-italic.woff2"
  done
  copy_legacy_font "noto-serif-display-$SUBSET-variable-wghtOnly-normal.woff2" "noto-serif-display-$SUBSET-wght-normal.woff2"
  copy_legacy_font "noto-serif-display-$SUBSET-variable-wghtOnly-italic.woff2" "noto-serif-display-$SUBSET-wght-italic.woff2"
done

# nunito (variable, woff2 only)
for WEIGHT in regular 700 900 ; do
  copy_legacy_font "nunito-v14-latin-ext_latin-$WEIGHT.woff2" "nunito-latin-wght-normal.woff2"
done
copy_legacy_font "nunito-v14-latin-ext_latin-italic.woff2" "nunito-latin-wght-italic.woff2"

# nunito-sans (variable, woff2 only)
for WEIGHT in regular 700 ; do
  copy_legacy_font "nunito-sans-v6-latin-$WEIGHT.woff2" "nunito-sans-latin-wght-normal.woff2"
done

# open-sans (variable, woff2 only)
for WEIGHT in regular 600 ; do
  copy_legacy_font "open-sans-v18-latin-$WEIGHT.woff2" "open-sans-latin-wght-normal.woff2"
done
for WEIGHT in 700 800 ; do
  copy_legacy_font "open-sans-v20-latin-ext_latin-$WEIGHT.woff2" "open-sans-latin-ext-wght-normal.woff2"
done
copy_legacy_font "open-sans-v20-latin-ext_latin-600italic.woff2" "open-sans-latin-ext-wght-italic.woff2"

# oswald (variable, woff2 only)
for SUBSET in latin latin-ext ; do
  for WEIGHT in 200 300 400 500 600 700 ; do
    copy_legacy_font "oswald-$SUBSET-$WEIGHT-normal.woff2" "oswald-$SUBSET-wght-normal.woff2"
  done
  copy_legacy_font "oswald-$SUBSET-variable-wghtOnly-normal.woff2" "oswald-$SUBSET-wght-normal.woff2"
done

# poiret-one (static)
for EXT in woff woff2 ; do
  copy_legacy_font "poiret-one-v9-latin-regular.$EXT" "poiret-one-latin-400-normal.$EXT"
done

# raleway (variable, woff2 only)
for WEIGHT in regular 700 ; do
  copy_legacy_font "raleway-v18-latin-ext_latin-$WEIGHT.woff2" "raleway-latin-wght-normal.woff2"
done

# sono (variable, woff2 only)
for SUBSET in latin latin-ext ; do
  for WEIGHT in 200 300 400 500 600 700 800 ; do
    copy_legacy_font "sono-$SUBSET-$WEIGHT-normal.woff2" "sono-$SUBSET-wght-normal.woff2"
  done
  copy_legacy_font "sono-$SUBSET-variable-wghtOnly-normal.woff2" "sono-$SUBSET-wght-normal.woff2"
done

# source-code-pro (variable, woff2 only)
for PAIR in "regular normal" "italic italic" "700 normal" "700italic italic" ; do
  LEGACY=$(echo $PAIR | cut -d ' ' -f 1)
  STYLE=$(echo $PAIR | cut -d ' ' -f 2)
  copy_legacy_font "source-code-pro-v13-latin-$LEGACY.woff2" "source-code-pro-latin-wght-$STYLE.woff2"
done

echo "Copying CSS to '$SITE_CSS'"
cp -n $CSS_DIR/* $SITE_CSS ||/usr/bin/true
cp -n $SCSS_DIR/* $SITE_SCSS ||/usr/bin/true
echo "Copying Fonts to '$SITE_FONTS'"
cp -n $FONT_DIR/* $SITE_FONTS ||/usr/bin/true
