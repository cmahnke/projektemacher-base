#!/usr/bin/env bash

if [ "$CI" = 'true' ] ; then
  # Python dependencies
  pip install -r ./themes/projektemacher-base/requirements.txt
fi
