#!/bin/sh

PACKAGE_DEPENDENCIES="py3-matplotlib py3-numpy py3-pillow py3-yaml py3-pytoml py3-termcolor py3-wheel"

echo "Installing '$PACKAGE_DEPENDENCIES' from distro repository"
sudo apt-get install $PACKAGE_DEPENDENCIES

CTX_PATH="$(dirname $(realpath $0))"
THEME_PATH=$(realpath --relative-to="$(cd $CTX_PATH/../../../..; echo $PWD)" $CTX_PATH/../..)

if [ -d $THEME_PATH ] ; then
    SEARCH_PATH=$THEME_PATH
else
    SEARCH_PATH=$CTX_PATH
fi

python -m pip install --upgrade pip
for REQUIREMENTS in `find $SEARCH_PATH/../../ -iname "requirements.txt"`
do
    PYTHON_DEPENDENCIES=`cat $REQUIREMENTS | tr '\n' ' '`
    echo "Installing Python modules '$PYTHON_DEPENDENCIES' from '$REQUIREMENTS'"
    pip install -r "$REQUIREMENTS"
done
