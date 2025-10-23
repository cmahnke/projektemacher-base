#!/usr/bin/env bash

JSON_PREFIX=content

if [ -z "$DEPENDENCY_MANAGER" ] ; then
  DEPENDENCY_MANAGER=npm
fi

CONVERT_SCRIPT="$DEPENDENCY_MANAGER run obj2gltf"

set -e -o pipefail

for FILE in `find $JSON_PREFIX -iname '*.json'`
do
  echo "Checking $FILE"
  if [ "$DEPENDENCY_MANAGER" = "npm" ] ; then
    npx eslint -c themes/projektemacher-base/eslint.config.mjs $FILE
  else
    $DEPENDENCY_MANAGER run eslint -c themes/projektemacher-base/eslint.config.mjs $FILE
  fi
done
