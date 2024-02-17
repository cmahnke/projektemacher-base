#!/usr/bin/env bash

OBJ_PREFIX=content
CONVERT_SCRIPT="yarn run obj2gltf"
COMPRESS_SCRIPT="yarn run gltf-pipeline"
METADATA_SCRIPT="yarn run gltf-transform xmp"
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
      $METADATA_SCRIPT $GLB "metadata-$GLB" --packet $METADATA
      rm $GLB
      mv "metadata-$GLB" $GLB
    fi

done
