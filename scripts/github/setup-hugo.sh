#!/bin/sh

set -e

DEFAULT_VARIANT="extended_"
DEFAULT_OS="linux"
DEFAULT_ARCH="amd64"

if [ -z "$VARIANT" ] ; then
  VARIANT=$DEFAULT_VARIANT
fi

if [ -z "$OS" ] ; then
  OS=$DEFAULT_OS
fi

if [ -z "$ARCH" ] ; then
  ARCH=$DEFAULT_ARCH
fi

case "$1" in
  http*)
    URL="$1"
    ARCHIVE="$(basename "$URL")"
    if [ -n "$HUGO_VERSION" ] ; then
      if [ "$(expr "$URL" : ".*$HUGO_VERSION")" -eq 0 ]; then
        echo "Version mismatch between '$HUGO_VERSION' and '$URL'"
        exit 1
      fi
    fi
    ;;
  *)
    if [ -n "$1" ] ; then
      HUGO_VERSION="$1"
    fi

    if [ -z "$HUGO_VERSION" ] ; then
      echo "HUGO_VERSION not set, exiting"
      exit 2
    fi

    ARCHIVE="hugo_${VARIANT}${HUGO_VERSION}_${OS}-${ARCH}.tar.gz"
    URL="https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/${ARCHIVE}"
    ;;
esac

echo "Using '$URL' to get '$ARCHIVE'"

curl -sLJO "${URL}"
mkdir -p "${HOME}/.local/hugo" "${HOME}/.local/bin"
#echo "PATH is '$PATH'"
tar -C "${HOME}/.local/hugo" -xf "${ARCHIVE}"
mv "${HOME}/.local/hugo/hugo" "${HOME}/.local/bin/"
rm -r "${ARCHIVE}" "${HOME}/.local/hugo"
echo "${HOME}/.local/bin/hugo" >> "${GITHUB_PATH}"


if ! [ -x "$(command -v hugo)" ]; then
  echo "'hugo' not installed"
  exit 3
else
  echo "Hugo: $(hugo version)"
fi

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
