#!/usr/bin/env bash

PDFJS_STATIC_DIR=static/pdfjs
PDFJS_URL=https://github.com/mozilla/pdf.js
TMP_DIR=tmp-pdfjs
CWD=`pwd`

if [ -z "$DEPENDENCY_MANAGER" ] ; then
  DEPENDENCY_MANAGER=npm
fi

if test -r yarn.lock ; then
    PDFJS_VERSION=$(grep /pdfjs-dist yarn.lock |sed -E 's/.*pdfjs-dist-(.*).tgz.*/\1/g')
else
    PDFJS_VERSION=master
fi

if [ -d "$TMP_DIR" ] ; then
    echo "'$TMP_DIR' already exists - deleting"
    rm -rf "$TMP_DIR"
fi

mkdir -p "$PDFJS_STATIC_DIR" "$TMP_DIR"
git clone --depth 1 --branch "v$PDFJS_VERSION" https://github.com/mozilla/pdf.js "$TMP_DIR"

cd "$TMP_DIR"
$DEPENDENCY_MANAGER install --ignore-scripts
$DEPENDENCY_MANAGER run gulp generic

cd "$CWD"
rm -rf static/pdfjs/*
mv $TMP_DIR/build/generic/* "$PDFJS_STATIC_DIR"

rm -rf "$TMP_DIR"
