#!/usr/bin/env bash

set -e -o pipefail

CTX_PATH="$(dirname $(realpath $0))"


cd $CTX_PATH/../PyHugo

pip install -r requirements.txt
python setup.py install
