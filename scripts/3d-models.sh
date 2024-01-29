#!/usr/bin/env bash

OBJ_PREFIX=content
CONVERT_SCRIPT="yarn run obj2gltf"
COMPRESS_SCRIPT="yarn run gltf-pipeline"
DRACO=false

for FILE in `find $OBJ_PREFIX -iname '*.obj'`
do
    DIR=`dirname $FILE`
    GLTF="$DIR/"`basename $FILE .obj`".gltf"
    GLB="$DIR/"`basename $FILE .obj`".glb"
    echo "Converting $FILE in $DIR to $GLTF"
    if [ "$DRACO" = true ] ; then
      $CONVERT_SCRIPT -i "$FILE" -o "$GLTF"
      $COMPRESS_SCRIPT -i "$GLTF" -b -d -o "$GLB"
    else
      $CONVERT_SCRIPT -i "$FILE" -b -o "$GLB"
    fi
done
