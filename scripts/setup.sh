#!/usr/bin/env bash

if [ -z "$DEPENDENCY_MANAGER" ] ; then
  DEPENDENCY_MANAGER=npm
fi

$DEPENDENCY_MANAGER install --ignore-scripts

if [ -d "exampleSite" ]; then
  ./scripts/init/i18n.sh i18n
fi
