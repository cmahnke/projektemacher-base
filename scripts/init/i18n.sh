#!/usr/bin/env bash
#
# Merges i18n fragments named '<id>.<lang>.toml' into '<lang>.toml' and deletes
# the fragments afterwards. The merged files are gitignored, the fragments are
# tracked. MUST be run before building multilingual sites (exampleSite, CI) —
# if fragments are present at build time, Hugo's multilingual i18n loader fails
# with '"art-x-<id>.<lang>": language: tag is not well-formed' because it parses
# the filename as a BCP47 language tag. See README.md, section 'i18n language
# files'. Note: when '<lang>.toml' already exists this script skips everything,
# so stale fragments are NOT removed — delete them manually in that case.

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
