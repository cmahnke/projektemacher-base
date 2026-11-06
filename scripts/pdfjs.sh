#!/usr/bin/env bash

set -e -o pipefail

PDFJS_STATIC_DIR=static/pdfjs
PDFJS_URL=https://github.com/mozilla/pdf.js
TMP_DIR=tmp-pdfjs
CWD=`pwd`

if [ -z "$DEPENDENCY_MANAGER" ] ; then
  DEPENDENCY_MANAGER=npm
fi

# Determine the pdf.js version to build: prefer the installed pdfjs-dist
# package (this directory or, when run from an exampleSite subdirectory,
# the parent one), then the lockfiles. Never fall back to a moving target
# like 'master' - the built viewer has to match the pdfjs-dist version
# used by the site's dependencies (see assets/ts/pdf-viewer.ts).
PDFJS_VERSION=''
if test -r node_modules/pdfjs-dist/package.json ; then
    PDFJS_VERSION=$(node -p "require('./node_modules/pdfjs-dist/package.json').version" || true)
elif test -r ../node_modules/pdfjs-dist/package.json ; then
    PDFJS_VERSION=$(node -p "require('../node_modules/pdfjs-dist/package.json').version" || true)
elif test -r yarn.lock ; then
    PDFJS_VERSION=$(grep /pdfjs-dist yarn.lock | sed -E 's/.*pdfjs-dist-(.*).tgz.*/\1/g' || true)
elif test -r package-lock.json ; then
    PDFJS_VERSION=$(node -p "require('./package-lock.json').packages['node_modules/pdfjs-dist'].version" 2>/dev/null || true)
fi

if [ -z "$PDFJS_VERSION" ] ; then
    echo "Couldn't determine the pdfjs-dist version - none of node_modules/pdfjs-dist, yarn.lock or package-lock.json was found or parseable, exiting!" >&2
    exit 1
fi

echo "Building pdf.js viewer for version $PDFJS_VERSION"

if [ -d "$TMP_DIR" ] ; then
    echo "'$TMP_DIR' already exists - deleting"
    rm -rf "$TMP_DIR"
fi

mkdir -p "$PDFJS_STATIC_DIR" "$TMP_DIR"
git clone --depth 1 --branch "v$PDFJS_VERSION" https://github.com/mozilla/pdf.js "$TMP_DIR"

cd "$TMP_DIR"
$DEPENDENCY_MANAGER install --ignore-scripts
./node_modules/.bin/gulp generic

cd "$CWD"
rm -rf static/pdfjs/*
mv $TMP_DIR/build/generic/* "$PDFJS_STATIC_DIR"

rm -rf "$TMP_DIR"
