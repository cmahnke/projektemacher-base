#!/bin/sh
PYTHON_DEPENDENCIES="pillow termcolor pyyaml toml icalendar"

echo "Installing Python modules $PYTHON_DEPENDENCIES"

python -m pip install --upgrade pip
pip install $PYTHON_DEPENDENCIES
