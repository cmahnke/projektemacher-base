#!/usr/bin/env bash

echo "Merging language files"

CTX_PATH="$(dirname $(realpath $0))"
THEME_PATH=$(realpath --relative-to="$(cd $CTX_PATH/../../../..; echo $PWD)" $CTX_PATH/../..)

if [ -z "$1" ] ; then
  LANG_DIR=$THEME_PATH/i18n
else
  LANG_DIR=$1
fi

SED=sed
OS="`uname`"
case "$OS" in
  'Darwin')
    SED=gsed
    ;;
  'Linux')
    SED=sed
    ;;
esac
echo "OS is '$OS', sed is '$SED'"

LANGS=`ls -1 $LANG_DIR/*.*.toml | $SED -E 's/.*?\.(.*?)\.toml/\1/g'|sort|uniq`

for LANG in $LANGS
do
  echo "Merging language files for '$LANG'"
  if [ -r "$LANG_DIR/$LANG.toml" ] ; then
    echo "'$LANG.toml' already exists, skipping"
  else
    cat $LANG_DIR/*.$LANG.toml >> $LANG_DIR/$LANG.toml
    echo "Deleting "`ls $LANG_DIR/*.$LANG.toml`
    rm $LANG_DIR/*.$LANG.toml
  fi
done
