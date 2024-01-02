#!/usr/bin/env bash

if [ -z "$IMAGES" ] ; then
  IMAGES=$(find content -name '*.svg')
fi

if [ -z "`which jq`" ] ; then
  echo "jq is needed for sanity check"
  exit 2
fi

if [ -n "`jq -r '.scripts.svgo' package.json`" ] ; then
  echo "Error: svgo command gets overwritten in package.json"
  exit 1
fi

IFS=$(echo -en "\n\b")
for IMAGE in $IMAGES
do
    IMAGE_PREFIX=$(basename "$IMAGE" .svg)
    TMP_FILE=${IMAGE_PREFIX}.tmp

    echo "Processing '$IMAGE'..."
    yarn run svgo --config ./config/svgo.config.js -i "$IMAGE" -o "$TMP_FILE" --multipass
    rm "$IMAGE"
    mv "$TMP_FILE" "$IMAGE"

done
