#!/usr/bin/env bash

set -e -o pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
. $SCRIPT_DIR/../node/dependency-management.sh

#NPM dependencies
echo "Generating package.json"
if ! which jq &> /dev/null ; then
    echo "jq could not be found, exiting"
    exit 123
fi

if ! git diff --name-only --exit-code package.json ; then
    git checkout package.json
fi

SED=sed
REALPATH=realpath
OS="`uname`"
case "$OS" in
  'Darwin')
    SED=gsed
    REALPATH=grealpath
    ;;
  'Linux')
    SED=sed
    REALPATH=realpath
    ;;
esac

if [ -z "$DEPENDENCY_MANAGER" ] ; then
  DEPENDENCY_MANAGER=npm
fi

if [ "$DEPENDENCY_MANAGER" = 'yarn' ] ; then
  YARN=`which yarn`
  if [ -z "$YARN" ] ; then
    #Try /usr/local/bin/yarn
    if [ -x /usr/local/bin/yarn ] ; then
      YARN=/usr/local/bin/yarn
    elif [ -x `npm root -g`/yarn/bin/yarn ] ; then
      YARN=`npm root -g`/yarn/bin/yarn
    else
      npm install -g yarn
      YARN='npm run yarn'
    fi
  fi
  echo "Using 'yarn' from '$YARN'"
fi

echo "OS is '$OS', sed is '$SED', realpath is '$REALPATH', dependency manager is '$DEPENDENCY_MANAGER'"

CTX_PATH="$(dirname $($REALPATH $0))"
THEME_PATH=$($REALPATH --relative-to="$(cd $CTX_PATH/../../../..; echo $PWD)" $CTX_PATH/../..)

# The order matters here - first all themes, then the file from this theme and then the one from the site itself
THEMES_PACKAGE_FILES="$(find themes -name package.hugo.json)"
THEME_PACKAGE_FILE="$(find $THEME_PATH -name package.json -not \( -path '*/node_modules/*' -o -path '*/fonts/*' -o -path '*/flags/*' \))"
SITE_PACKAGE_FILE="$(find .  -maxdepth 1 -name package.json -type f -size +0c)"
PACKAGE_FILES=$(echo $THEMES_PACKAGE_FILES $THEME_PACKAGE_FILE $SITE_PACKAGE_FILE | tr '\n' ' ')
echo "Merging $PACKAGE_FILES"

PACKAGE=$(jq -s 'reduce .[] as $d ({}; . *= $d)' $(echo $PACKAGE_FILES))
echo "$PACKAGE" > package.json

if [ -d patches ] ; then
    rm -rf patches
fi

if ! git ls-files --error-unmatch .stylelintrc.json &> /dev/null ; then
  cp ./themes/projektemacher-base/.stylelintrc.json .
fi

if ! git ls-files --error-unmatch browserslist &> /dev/null ; then
  cp ./themes/projektemacher-base/browserslist .
fi

if ! git ls-files --error-unmatch purgecss.config.js &> /dev/null ; then
  cp ./themes/projektemacher-base/purgecss.config.js .
fi

# Hugo >= 0.161 (gohugoio/hugo#14852) needs pnpm's hoisted linker
if [ "$DEPENDENCY_MANAGER" = 'pnpm' ] ; then
  if ! grep -Eq '^[[:space:]]*node-linker[[:space:]]*=[[:space:]]*hoisted' .npmrc 2>/dev/null ; then
    if grep -Eq '^[[:space:]]*node-linker[[:space:]]*=' .npmrc 2>/dev/null ; then
      # Has a different value - replace it
      $SED -i 's|^[[:space:]]*node-linker[[:space:]]*=.*|node-linker=hoisted|' .npmrc
    else
      # Not present - append it
      printf '\n# Required by Hugo >= 0.161 (gohugoio/hugo#14852)\nnode-linker=hoisted\n' >> .npmrc
    fi
  fi
else
  # npm and yarn don't know pnpm's 'node-linker' setting (npm warns about an
  # unknown project config) - only write the settings they need
  if [ -f .npmrc ] ; then
    $SED -i '/^[[:space:]]*node-linker[[:space:]]*=/d' .npmrc
  else
    printf 'legacy-peer-deps=true\n' > .npmrc
  fi
  if ! grep -Eq '^[[:space:]]*legacy-peer-deps[[:space:]]*=' .npmrc ; then
    printf '\nlegacy-peer-deps=true\n' >> .npmrc
  fi
fi

if [ "$DEPENDENCY_MANAGER" = 'yarn' ] ; then
  yarn config set ignore-engines true
  INSTALL_OPTS="--ignore-engines"
  $YARN install $INSTALL_OPTS
  ERR=$?
else
  $DEPENDENCY_MANAGER install
  ERR=$?
fi

if [ $ERR -ne 0 ] ; then
    echo "yarn install failed with $ERR"
    cat package.json | jq -C .
    if [ -r yarn-error.log ] ; then
        cat yarn-error.log
    fi
    exit $ERR
fi

# Install the browsers used by Puppeteer; uses the build pinned by the installed
# puppeteer package and is a no-op if they are already in the cache
if grep -q '"puppeteer"' package.json ; then
    npx puppeteer browsers install chrome
    npx puppeteer browsers install chrome-headless-shell
fi
