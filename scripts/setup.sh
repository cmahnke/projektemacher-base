#!/usr/bin/env bash

yarn install --ignore-scripts

if [ -d "exampleSite" ]; then
  ./scripts/init/i18n.sh i18n
fi
