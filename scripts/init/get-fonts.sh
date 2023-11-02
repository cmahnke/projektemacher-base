#!/usr/bin/env bash

echo "Getting fonts"

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

$THEME_PATH/scripts/fonts.sh $THEME_PATH
