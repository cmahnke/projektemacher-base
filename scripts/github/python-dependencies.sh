#!/bin/sh

# Disable the need for pyenv and externally managed stuff - we are on a throwaway system:
printf "[global]\nbreak-system-packages = true\n" >> ~/.config/pip/pip.conf
sudo find /usr/lib -name EXTERNALLY-MANAGED -exec rm -f {} \;

PACKAGE_DEPENDENCIES="python3-matplotlib python3-numpy python3-pillow python3-yaml python3-pytoml python3-termcolor python3-wheel python3-cairosvg python3-icalendar cython3 python3-opencv"

echo "Installing '$PACKAGE_DEPENDENCIES' from distro repository"
sudo apt-get update
sudo apt-get install --fix-missing $PACKAGE_DEPENDENCIES

CTX_PATH="$(dirname $(realpath $0))"
THEME_PATH=$(realpath --relative-to="$(cd $CTX_PATH/../../../..; echo $PWD)" $CTX_PATH/../..)

if [ -d $THEME_PATH ] ; then
    SEARCH_PATH=$THEME_PATH
else
    SEARCH_PATH=$CTX_PATH
fi

python -m pip install --upgrade pip
set -e
# TODO: this fails if path contains a space (' ') character
echo "Searching for requirements.txt in '$SEARCH_PATH'"
for REQUIREMENTS in `find $SEARCH_PATH/../../ -iname "requirements.txt"`
do
    PYTHON_DEPENDENCIES=`cat $REQUIREMENTS | tr '\n' ' '`
    echo "Installing Python modules '$PYTHON_DEPENDENCIES' from '$REQUIREMENTS'"
    pip install -r "$REQUIREMENTS"
done
