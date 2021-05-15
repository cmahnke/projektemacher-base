#!/bin/sh
PYTHON_DEPENDENCIES="pillow termcolor pyyaml toml"

echo "Installing Python modules $PYTHON_DEPENDENCIES"

# We currently use Ububtu 18.04 which ships an quit old python version - this is thew reason why we use the GitHub Python action to setup Python itself

python -m pip install --upgrade pip
pip install $PYTHON_DEPENDENCIES
