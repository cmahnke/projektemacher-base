#!/usr/bin/env bash

PYTHON_PATH=/opt/homebrew/bin/
PYTHON_VERSION=3.10

brew install jpeg-xl
LDFLAGS="-L/opt/homebrew/lib/" CPPFLAGS="-I/opt/homebrew/include/" $PYTHON_PATH/pip$PYTHON_VERSION install git+https://github.com/olokelo/jxlpy

$PYTHON_PATH/pip$PYTHON_VERSION install Pillow==9.5.0
