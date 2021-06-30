#!/usr/bin/env bash

PDFJS_STATIC_DIR=static/pdfjs
PDFJS_URL=https://github.com/mozilla/pdf.js
TMP_DIR=tmp-pdfjs
CWD=`pwd`

if test -r yarn.lock ; then
    PDFJS_VERSION=$(grep /pdfjs-dist yarn.lock |sed -E 's/.*pdfjs-dist-(.*).tgz.*/\1/g')
else
    PDFJS_VERSION=master
fi

mkdir -p "$PDFJS_STATIC_DIR" "$TMP_DIR"
git clone --branch "v$PDFJS_VERSION" https://github.com/mozilla/pdf.js "$TMP_DIR"

cd "$TMP_DIR"
yarn install --ignore-scripts
yarn run gulp generic

cd "$CWD"
rm -rf static/pdfjs/*
mv $TMP_DIR/build/generic/* "$PDFJS_STATIC_DIR"

rm -rf "$TMP_DIR"
