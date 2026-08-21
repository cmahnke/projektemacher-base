#!/usr/bin/env bash

set -e -o pipefail

echo "Set sane npm defaults"
npm config set audit false
npm config set fund false
