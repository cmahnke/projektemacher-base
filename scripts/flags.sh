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

BASE=$THEME_PATH/flags
SCSS_DIR="$BASE/scss"
SITE_SCSS=assets/scss/flags/
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

mkdir -p $SITE_SCSS

rm -f fonts/out/css/@*
echo "Copying SCSS to '$SITE_SCSS'"
cp -n $SCSS_DIR/* $SITE_SCSS ||/usr/bin/true
