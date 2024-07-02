#!/usr/bin/env bash

OS="`uname`"
case "$OS" in
  'Darwin')
    if [ $(uname -m) == 'arm64' ]; then
        npm install -g --force --cpu=arm64 --os=darwin sharp
    fi
    ;;
  'Linux')
    if [ $(cat /etc/os-release | grep "NAME=" | grep -ic "Alpine") -gt 0 ] ; then
      npm install -g --force --cpu=x64 --os=linux --libc=musl sharp
    else
      npm install -g --force --cpu=x64 --os=linux --libc=glibc sharp
    fi
    ;;
esac
