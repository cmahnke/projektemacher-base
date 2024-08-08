#!/usr/bin/env bash
JXLPY="git+https://github.com/olokelo/jxlpy"

CTX=`dirname $0`
PYTHON=`$CTX/./find-python3.sh`
PYTHON_PATH=`dirname $PYTHON`
PYTHON_VERSION=`$PYTHON --version | cut -d' ' -f2 | cut -d'.' -f1,2`

echo "Using $PYTHON, at $PYTHON_PATH, version $PYTHON_VERSION"

brew install jpeg-xl

$PYTHON_PATH/pip$PYTHON_VERSION install --break-system-packages Pillow
LDFLAGS="-L/opt/homebrew/lib/" CPPFLAGS="-I/opt/homebrew/include/" $PYTHON_PATH/pip$PYTHON_VERSION install --break-system-packages $JXLPY
