#!/usr/bin/env bash


if ! command -v npm 2>&1 >/dev/null
then
    echo "npm could not be found"
    exit 1
fi
if ! command -v pnpm 2>&1 >/dev/null
then
    echo "pnpm could not be found"
    exit 1
fi
if ! command -v yarn 2>&1 >/dev/null
then
    echo "yarn could not be found"
    exit 1
fi

if [ -z "$DEPENDENCY_MANAGER" ] ; then
  DEPENDENCY_MANAGER=pnpm
fi

if [ "$DEPENDENCY_MANAGER" = 'pnpm' ] ; then
  npm i -g pnpm
fi

INSTALL_OPTS=""
EXECUTOR=""
if [ "$DEPENDENCY_MANAGER" = 'npm' ] ; then
  MANAGER_OPTS="--no-audit"
  EXECUTOR=npx
fi

if [ "$DEPENDENCY_MANAGER" = 'pnpm' ] ; then
  EXECUTOR=pnpx
fi

export DEPENDENCY_MANAGER MANAGER_OPTS EXECUTOR
