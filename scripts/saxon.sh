#!/usr/bin/env bash

if [ -z "$SAXON" ] ; then
  SAXON=`which saxon`
fi

if [ -z "$SAXON" ] ; then
  SAXON="java -jar /opt/saxon/saxon.jar"
fi

if [ -z "$SAXON" ] ; then
  echo "Could't find saxon script"
  exit 1
fi

$SAXON "$@"
