#!/usr/bin/env bash

for CANDIDATE in `which -a python3`
do
  if [[ $CANDIDATE != *"anaconda"* ]] ; then
      echo "$CANDIDATE"
      break
  fi
done
