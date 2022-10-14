#!/bin/sh

CTX_PATH="$(dirname $(realpath $0))"
THEME_PATH=$(realpath --relative-to="$(cd $CTX_PATH/../../../..; echo $PWD)" $CTX_PATH/../..)

PUPPETEER_EXPERIMENTAL_CHROMIUM_MAC_ARM=true node $THEME_PATH/scripts/check-js-browser-errors.js 
