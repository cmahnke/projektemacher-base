#!/usr/bin/env bash

SAXON_DIR="/opt/saxon"

if [ -z "$SAXON" ] ; then
  SAXON=`which saxon`
fi

if [ -z "$SAXON" ] ; then
  SAXON="java -Xmx1024m -cp $SAXON_DIR/saxon.jar:$SAXON_DIR/xmlresolver.jar net.sf.saxon.Transform"
fi

if [ -z "$SAXON" ] ; then
  echo "Could't find saxon script"
  exit 1
fi

$SAXON "$@"
