#!/usr/bin/env bash

set -e

OBJ_PREFIX=content

if [ -z "$DEPENDENCY_MANAGER" ] ; then
  DEPENDENCY_MANAGER=npm
fi

if [ "$DEPENDENCY_MANAGER" = "npm" ] ; then
  CONVERT_SCRIPT="npx obj2gltf"
  COMPRESS_SCRIPT="npx gltf-pipeline"
  METADATA_SCRIPT="npx gltf-transform xmp"
else
  CONVERT_SCRIPT="$DEPENDENCY_MANAGER run obj2gltf"
  COMPRESS_SCRIPT="$DEPENDENCY_MANAGER run gltf-pipeline"
  METADATA_SCRIPT="$DEPENDENCY_MANAGER run gltf-transform xmp"
fi

DRACO=false

for FILE in `find $OBJ_PREFIX -iname '*.obj'`
do
    DIR=`dirname $FILE`
    BASENAME=`basename $FILE .obj`
    METADATA="$DIR/$BASENAME.json"
    GLTF="$DIR/$BASENAME.gltf"
    GLB="$DIR/$BASENAME.glb"
    echo "Converting $FILE in $DIR to $GLTF"
    if [ "$DRACO" = true ] ; then
      $CONVERT_SCRIPT -i "$FILE" -o "$GLTF"
      $COMPRESS_SCRIPT -i "$GLTF" -b -d -o "$GLB"
    else
      $CONVERT_SCRIPT -i "$FILE" -b -o "$GLB"
    fi

    if [ -r $METADATA ] ; then
      echo "Adding metadata from $METADATA to $GLB"
      META_GLB="$DIR/meta-$BASENAME.glb"
      $METADATA_SCRIPT $GLB "$META_GLB" --packet $METADATA
      rm $GLB
      mv "$META_GLB" $GLB
    fi

done
