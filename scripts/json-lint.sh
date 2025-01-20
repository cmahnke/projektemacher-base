#!/usr/bin/env bash

JSON_PREFIX=content
CONVERT_SCRIPT="yarn run obj2gltf"

set -e -o pipefail

for FILE in `find $JSON_PREFIX -iname '*.json'`
do
  echo "Checking $FILE"
  yarn run eslint -c themes/projektemacher-base/eslint.config.mjs $FILE
done
