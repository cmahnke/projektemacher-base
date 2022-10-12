#!/bin/sh

echo "Trying to set up Dart Sass"

DARTSASS_VERSION=1.55.0
BIN_DIR=/usr/local/bin

case "`uname`" in
  'Darwin')
    OS=macos
    ;;
  'Linux')
    OS=linux
    ;;
esac

ARCH="x64"
case "`uname -m`" in
  'x86_64')
    ARCH=x64
    ;;
  'arm64')
    ARCH=arm64
    ;;
  'arm')
    ARCH=arm
    ;;
esac

DARTSASS_URL="https://github.com/sass/dart-sass-embedded/releases/download/${DARTSASS_VERSION}/sass_embedded-${DARTSASS_VERSION}-${OS}-${ARCH}.tar.gz"


echo "Downloading ${DARTSASS_URL}"

curl -LJO "${DARTSASS_URL}"

tar -xvf sass_embedded-${DARTSASS_VERSION}-${OS}-${ARCH}.tar.gz
sudo mv sass_embedded/dart-sass-embedded $BIN_DIR
rm -rf sass_embedded*;
