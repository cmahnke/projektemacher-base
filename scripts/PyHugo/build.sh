#!/bin/sh

mkdir -p ./PyHugolib/build

cd go
GOMOD=`pwd` go build -buildmode=c-shared  -o ../PyHugolib/build/hugolib.so ./hugolib.go
