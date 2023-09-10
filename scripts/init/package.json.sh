#!/usr/bin/env bash

#NPM dependencies
echo "Generating package.json"
if ! which jq &> /dev/null ; then
    echo "jq could not be found, exiting"
    exit 123
fi

if ! git diff --name-only --exit-code package.json ; then
    git checkout package.json
fi

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

# The order matters here - first all themes, then the file from this theme and then the one from the site itself
THEMES_PACKAGE_FILES="$(find themes -name package.hugo.json)"
THEME_PACKAGE_FILE="$(find $THEME_PATH -name package.json -not -path '*/node_modules/*')"
SITE_PACKAGE_FILE="$(find .  -maxdepth 1 -name package.json -type f -size +0c)"
PACKAGE_FILES=$(echo $THEMES_PACKAGE_FILES $THEME_PACKAGE_FILE $SITE_PACKAGE_FILE | tr '\n' ' ')
echo "Merging $PACKAGE_FILES"

PACKAGE=$(jq -s 'reduce .[] as $d ({}; . *= $d)' $(echo $PACKAGE_FILES))
echo "$PACKAGE" > package.json

OS="`uname`"
ARCH="`uname -m`"
if [ "$OS" = 'Darwin' ] ; then
    if [ "$ARCH" = 'arm64' ] ; then
        echo "OS is '$OS', Architecture is '$ARCH'"
        export PUPPETEER_EXPERIMENTAL_CHROMIUM_MAC_ARM=true
    fi
fi

if [ -d patches ] ; then
    rm -rf patches
fi

yarn install
ERR=$?
if [ $ERR -ne 0 ] ; then
    echo "yarn install failed with $ERR"
    cat package.json | jq -C .
    if [ -r yarn-error.log ] ; then
        cat yarn-error.log
    fi
    exit $ERR
fi

if [ -z "$(ls -A ./node_modules/puppeteer-core/.local-chromium/)" ]; then
    echo "Chrome dependency seems to be missing, downloading again!"
    if [ grep puppeteer package.json ] ; then
        cd node_modules/puppeteer
        node install.js
        cd ../..
    fi
fi
