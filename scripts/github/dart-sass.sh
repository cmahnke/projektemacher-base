#!/bin/sh

echo "Trying to set up Dart Sass"
# Last known working is 1.92.1
DARTSASS_VERSION=1.94.2
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

DARTSASS_URL="https://github.com/sass/dart-sass/releases/download/${DARTSASS_VERSION}/dart-sass-${DARTSASS_VERSION}-${OS}-${ARCH}.tar.gz"
#DARTSASS_URL="https://github.com/sass/dart-sass-embedded/releases/download/${DARTSASS_VERSION}/sass_embedded-${DARTSASS_VERSION}-${OS}-${ARCH}.tar.gz"


echo "Downloading ${DARTSASS_URL}"

curl -LJO "${DARTSASS_URL}"

tar -xvf dart-sass-${DARTSASS_VERSION}-${OS}-${ARCH}.tar.gz
sudo cp -r dart-sass/* $BIN_DIR
rm -rf dart-sass*;

sass --version
