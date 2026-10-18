#!/usr/bin/env bash

set -e -o pipefail

REALPATH=realpath
OS="`uname`"
case "$OS" in
  'Darwin')
    REALPATH=grealpath
    ;;
  'Linux')
    REALPATH=realpath
    ;;
esac

CTX_PATH="$(dirname $($REALPATH $0))"
THEME_PATH=$($REALPATH "$CTX_PATH/../..")

# Run the checker from the exampleSite directory, it contains both the Hugo
# configuration and the built site (publishDir 'docs') as well as the URL
# configuration
cd "$THEME_PATH/exampleSite"

# Pages whose JS requires WebGL or WebGPU are deliberately not listed in
# test-urls.json, since 3D APIs are disabled by default (see the '-g' flag)
ERR=0
node "$THEME_PATH/scripts/check-js-browser-errors.mjs" -f -c test-urls.json "$@" || ERR=$?
if [ $ERR -ne 0 ] ; then
    echo "ERROR! Page contains loading (124) or JS (123) errors: $ERR"
    exit $ERR
fi
