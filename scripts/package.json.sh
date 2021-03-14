#!/usr/bin/env bash

#NPM dependencies
echo "Generating package.json"
if ! which jq &> /dev/null ; then
    echo "jq could not be found, exiting"
    exit 123
fi
if test -f package.json ; then
    rm package.json
fi

PACKAGE_FILES="$(find . -name package.hugo.json) $(find . -name package.json -depth 0 -size +0c )"
PACKAGE_FILES=`echo $PACKAGE_FILES | tr '\n' ' '`
echo "Merging $PACKAGE_FILES"

jq -s add $PACKAGE_FILES > package.json
if ! yarn install ; then
    ERR=$?
    cat package.json | jq -C .
    cat yarn-error.log
    exit $ERR
fi
