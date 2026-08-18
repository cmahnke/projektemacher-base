#!/usr/bin/env bash

set -e -o pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

SAXON_DIR="/opt/saxon"
SAXON_SCRIPT="$SAXON_DIR/saxon"

if [ -z "$SAXON" ] ; then
  SAXON=`which saxon`
fi

if [ -x "$SAXON_SCRIPT" ] ; then
  SAXON=$SAXON_SCRIPT
fi

if [ -z "$SAXON" ] ; then
  SAXON="java -Xmx1024m -cp $SAXON_DIR/saxon.jar:$SAXON_DIR/xmlresolver.jar net.sf.saxon.Transform"
fi

if [ -z "$SAXON" ] ; then
  echo "Trying to instal Saxon"
  $SCRIPT_DIR/github/setup-xslt.sh
  SAXON=$SAXON_SCRIPT
fi

if [ -z "$SAXON" ] ; then
  echo "Could't find saxon script"
  exit 1
fi

echo "Running $SAXON $@"

$SAXON "$@"
