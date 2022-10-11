#!/usr/bin/env bash

PATCH_URL="https://github.com/ProjectMirador/mirador/pull/3029.patch"
rm -f 3029.patch
wget $PATCH_URL

rm -rf node_modules/mirador
yarn install --ignore-scripts --check-files

cd node_modules/mirador
#git am ../../3029.patch
patch -f -p1 -i ../../patches/mirador+3.3.0.patch
cd ../..
npx patch-package mirador

rm 3029.patch
