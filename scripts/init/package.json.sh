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

THEME_PACKAGE_FILES="$(find . -name package.hugo.json)"
SITE_PACKAGE_FILE="$(find .  -maxdepth 1 -name package.json -size +0c)"
PACKAGE_FILES=$(echo $THEME_PACKAGE_FILES $SITE_PACKAGE_FILE | tr '\n' ' ')
echo "Merging $PACKAGE_FILES"

PACKAGE=$(jq -s 'reduce .[] as $d ({}; . *= $d)' $(echo $PACKAGE_FILES))
echo "$PACKAGE" > package.json
if ! yarn install ; then
    ERR=$?
    cat package.json | jq -C .
    cat yarn-error.log
    exit $ERR
fi
