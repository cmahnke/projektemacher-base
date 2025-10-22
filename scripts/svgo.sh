#!/usr/bin/env bash

set -e

if [ -z "$DEPENDENCY_MANAGER" ] ; then
  DEPENDENCY_MANAGER=npm
fi

if [ -z "$IMAGES" ] ; then
  IMAGES=$(find content -name '*.svg')
fi

if [ -z "$IMAGES" ] ; then
  echo "No SVG Files found!"
  exit 0
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

if [ -z "$DEPENDENCY_MANAGER" ] ; then
  DEPENDENCY_MANAGER=npm
fi

if [ -n "$SVGO" ] ; then
  echo "Setting svgo binary externally has been disabled"
  exit 1
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

    if [ "$DEPENDENCY_MANAGER" = "npm" ] ; then
      npx svgo --config ./config/svgo.config.js -i "$IMAGE" -o "$TMP_FILE" --multipass
    else
      SVGO=`$DEPENDENCY_MANAGER bin svgo`
      $SVGO --config ./config/svgo.config.js -i "$IMAGE" -o "$TMP_FILE" --multipass
    fi


    if [ -z "$OUTDIR" ] ; then
      rm "$IMAGE"
      mv "$TMP_FILE" "$IMAGE"
    fi

done
