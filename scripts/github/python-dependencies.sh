#!/bin/sh

CTX_PATH="$(dirname $(realpath $0))"
THEME_PATH=$(realpath --relative-to="$(cd $CTX_PATH/../../../..; echo $PWD)" $CTX_PATH/../..)

python -m pip install --upgrade pip
for REQUIREMENTS in `find $THEME_PATH/../../ -iname "requirements.txt"`
do
    PYTHON_DEPENDENCIES=`cat $REQUIREMENTS | tr '\n' ' '`
    echo "Installing Python modules '$PYTHON_DEPENDENCIES' from '$REQUIREMENTS'"
    pip install -r "$REQUIREMENTS"
done
