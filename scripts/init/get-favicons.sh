#!/usr/bin/env bash

set -e -o pipefail

echo "Generating favicons"

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
echo "OS is '$OS', realpath is '$REALPATH'"

CTX_PATH="$(dirname $($REALPATH $0))"
THEME_PATH=$($REALPATH "$CTX_PATH/../..")

# Generate the example site's favicon set from the theme's 'cm.svg' — the
# same source and options the live projektemacher.org site uses. See
# scripts/favicon.sh for the generated files (they are gitignored).
cd "$THEME_PATH/exampleSite"
SOURCE="../static/images/cm.svg" OPTIONS="-transparent white" $THEME_PATH/scripts/favicon.sh
