#!/usr/bin/env bash

echo "Merging language files"

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
echo "OS is '$OS', sed is '$SED', realpath is '$REALPATH'"

CTX_PATH="$(dirname $($REALPATH $0))"
THEME_PATH=$($REALPATH --relative-to="$(cd $CTX_PATH/../../../..; echo $PWD)" $CTX_PATH/../..)

if [ -z "$1" ] ; then
  LANG_DIR=$THEME_PATH/i18n
else
  LANG_DIR=$1
fi


LANGS=`ls -1 $LANG_DIR/*.*.toml | $SED -E 's/.*?\.(.*?)\.toml/\1/g'|sort|uniq`

for LANG in $LANGS
do
  echo "Merging language files for '$LANG'"
  if [ -r "$LANG_DIR/$LANG.toml" ] ; then
    echo "'$LANG.toml' already exists, skipping"
  else
    echo "Merging: "`ls $LANG_DIR/*.$LANG.toml`" into $LANG_DIR/$LANG.toml"
    cat $LANG_DIR/*.$LANG.toml >> $LANG_DIR/$LANG.toml
    echo "Deleting "`ls $LANG_DIR/*.$LANG.toml`
    rm $LANG_DIR/*.$LANG.toml
  fi
done
