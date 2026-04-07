#!/bin/sh

set -e

DEFAULT_VARIANT="extended_"
DEFAULT_OS="linux"
DEFAULT_ARCH="amd64"

if [ -n "$1" ] ; then
  HUGO_VERSION="$1"
fi

if [ -z "$HUGO_VERSION" ] ; then
  echo "HUGO_VERSION not set, exiting"
fi

if [ -z "$VARIANT" ] ; then
  VARIANT=$DEFAULT_VARIANT
fi

if [ -z "$OS" ] ; then
  OS=$DEFAULT_OS
fi

if [ -z "$ARCH" ] ; then
  ARCH=$DEFAULT_ARCH
fi

curl -sLJO "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_${VARIANT}${HUGO_VERSION}_${OS}-${ARCH}.tar.gz"
mkdir "${HOME}/.local/hugo"
tar -C "${HOME}/.local/hugo" -xf "hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz"
rm "hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz"
echo "${HOME}/.local/hugo" >> "${GITHUB_PATH}"


echo "Hugo: $(hugo version)"

if ! [ -x "$(command -v sass)" ]; then
    echo "'sass' not installed"
else
  echo "Dart Sass: $(sass --version)"
fi

if ! [ -x "$(command -v go)" ]; then
  echo "'go' not installed"
else
  echo "Go: $(go version)"
fi


if ! [ -x "$(command -v node)" ]; then
  echo "'node' not installed"
else
  echo "Node.js: $(node --version)"
fi
