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

CTX_PATH="$(dirname $(realpath $0))"
THEME_PATH=$(realpath --relative-to="$(cd $CTX_PATH/../../../..; echo $PWD)" $CTX_PATH/../..)

# The order matters here - first all themes, then the file from this theme and then the one from the site itself
THEMES_PACKAGE_FILES="$(find themes -name package.hugo.json)"
THEME_PACKAGE_FILE="$(find $THEME_PATH -name package.json -not -path '*/node_modules/*')"
SITE_PACKAGE_FILE="$(find .  -maxdepth 1 -name package.json -type f -size +0c)"
PACKAGE_FILES=$(echo $THEMES_PACKAGE_FILES $THEME_PACKAGE_FILE $SITE_PACKAGE_FILE | tr '\n' ' ')
echo "Merging $PACKAGE_FILES"

PACKAGE=$(jq -s 'reduce .[] as $d ({}; . *= $d)' $(echo $PACKAGE_FILES))
echo "$PACKAGE" > package.json

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
