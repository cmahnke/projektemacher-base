#!/usr/bin/env bash

set -e

if [ -z "$IMAGES" ] ; then
  IMAGES=$(find content -name '*.svg')
fi

if [ -z "`which jq`" ] ; then
  echo "jq is needed for sanity check"
  exit 2
fi

if jq -e '.scripts.svgo' package.json ; then
  echo "Error: svgo command gets overwritten in package.json"
  exit 1
fi

if [ -n "$1" ] ; then
  OUTDIR="$1"
  echo "Using $OUTDIR as output directory"
fi

if [ -z "$SVGO" ] ; then
  SVGO=`yarn bin svgo`
fi

IFS=$(echo -en "\n\b")
for IMAGE in $IMAGES
do
    IMAGE_PREFIX=$(basename "$IMAGE" .svg)
    if [ -z "$OUTDIR" ] ; then
      TMP_FILE=${IMAGE_PREFIX}.tmp
    else
      TMP_FILE="$OUTDIR/`echo $IMAGE_PREFIX | tr '[:upper:]' '[:lower:]' | tr ' ' '-'`.svg"
    fi

    echo "Processing '$IMAGE' to '$TMP_FILE'"
    $SVGO --config ./config/svgo.config.js -i "$IMAGE" -o "$TMP_FILE" --multipass
    if [ -z "$OUTDIR" ] ; then
      rm "$IMAGE"
      mv "$TMP_FILE" "$IMAGE"
    fi

done
