#!/usr/bin/env bash

find content/post/ -name info.json -exec dirname {} \; | xargs rm -r
rm -rf docs/* node_modules resources/_gen
rm -rf static/images/favicon*
