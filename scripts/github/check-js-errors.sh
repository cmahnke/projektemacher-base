#!/bin/sh

CTX_PATH="$(dirname $(realpath $0))"
THEME_PATH=$(realpath --relative-to="$(cd $CTX_PATH/../../../..; echo $PWD)" $CTX_PATH/../..)

PUPPETEER_EXPERIMENTAL_CHROMIUM_MAC_ARM=true node $THEME_PATH/scripts/check-js-browser-errors.mjs -f
ERR=$?
if [ $ERR -ne 0 ] ; then
    echo "ERROR! Page contains loading (124) or JS (123) errors: $ERR"
    exit $ERR
fi
