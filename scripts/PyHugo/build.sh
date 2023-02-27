#!/bin/sh

mkdir -p ./PyHugolib/build
go build -buildmode=c-shared -o ./PyHugolib/build/hugolib.so hugolib.go
