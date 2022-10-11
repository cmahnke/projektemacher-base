#!/bin/sh

echo "Trying to set up Dart Sass"

DARTSASS_VERSION=1.55.0
OS="`uname | tr '[:upper:]' '[:lower:]'`"
ARCH="`uname -m`"
BIN_DIR=/usr/local/bin

mkdir -p $BIN_DIR

curl -LJO https://github.com/sass/dart-sass-embedded/releases/download/${DARTSASS_VERSION}/sass_embedded-${DARTSASS_VERSION}-${OS}-${ARCH}.tar.gz;

tar -xvf sass_embedded-${DARTSASS_VERSION}-${OS}-${ARCH}.tar.gz

sudo mv sass_embedded/dart-sass-embedded $BIN_DIR

rm -rf sass_embedded*;

dart-sass-embedded --vers
