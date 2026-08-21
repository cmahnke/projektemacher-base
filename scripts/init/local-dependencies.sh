#!/usr/bin/env bash

set -e -o pipefail

if [ "$CI" = 'true' ] ; then
  # Python dependencies
  pip install -r ./themes/projektemacher-base/requirements.txt
fi
