#!/usr/bin/env bash

PDFJS_STATIC_DIR=static/pdfjs
rm -rf $PDFJS_STATIC_DIR

find content/post/ -name info.json -not -path "*/*-hdr*" -not -path "*/*.hdr*" -exec dirname {} \; | xargs rm -r
rm -rf docs/* node_modules resources/_gen
rm -rf static/images/favicon*
find content/ -name ogPreview*.svg | xargs rm
find content/ -name ogPreview*.png | xargs rm
find content/ -name ogPreview*.jpg | xargs rm
find content/ -name vips-properties.xml | xargs rm

rm -rf node_modules

if [ -d themes/projektemacher-base/node_modules ] ; then
    echo "The directory contains 'node_modules' directory, you certainly are using this tree for theme development, this can have side effects, deleting!"
    rm -rf themes/projektemacher-base/node_modules
fi

git checkout package.json yarn.lock
# Cleanup and reset language files
git --git-dir themes/projektemacher-base/.git --work-tree themes/projektemacher-base clean -x -f i18n
git --git-dir themes/projektemacher-base/.git --work-tree themes/projektemacher-base checkout -f i18n
