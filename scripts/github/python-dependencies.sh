#!/bin/sh

CTX_PATH="$(dirname $(realpath $0))"
THEME_PATH=$(realpath --relative-to="$(cd $CTX_PATH/../../../..; echo $PWD)" $CTX_PATH/../..)

PYTHON_DEPENDENCIES=`cat $THEME_PATH/requirements.txt  | tr '\n' ' '`

echo "Installing Python modules $PYTHON_DEPENDENCIES"

python -m pip install --upgrade pip
pip install -r $THEME_PATH/requirements.txt
