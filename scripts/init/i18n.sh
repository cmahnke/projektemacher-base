#!/usr/bin/env bash

LANG_DIR=$1

LANGS=`ls -1 $LANG_DIR/*.*.toml | gsed -E 's/.*?\.(.*?)\.toml/\1/g'|sort|uniq`

for LANG in $LANGS
do
  echo "Merging language files for '$LANG'"
  if [ -r "$LANG_DIR/$LANG.toml" ] ; then
    echo "'$LANG.toml' already exists, skipping"
  else
    cat $LANG_DIR/*.$LANG.toml >> $LANG_DIR/$LANG.toml
    rm $LANG_DIR/*.$LANG.toml
  fi
done
