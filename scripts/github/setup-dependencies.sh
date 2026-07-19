#!/bin/sh
set -e

RUN_DEPENDENCIES="bash coreutils imagemagick parallel rsync sshpass bash jq findutils libcairo2-dev pkg-config poppler-utils	libvips-tools patchelf wget gifsicle libcairo2-dev libpango1.0-dev libgif-dev exiftool xmlstarlet librsvg2-bin"
DOCKER_DEPENDENCIES="moby-buildx moby-cli moby-engine"

sudo apt-get update
if [ "$( . /etc/lsb-release; echo $DISTRIB_RELEASE)" = "22.04" ] ; then
  echo "Marking Docker packages for holding"
  for pkg in docker-buildx-plugin docker-ce docker-ce-cli ; do sudo apt-mark hold $pkg; done
fi
if [ "$( . /etc/lsb-release; echo $DISTRIB_RELEASE)" = "24.04" ] ; then
  JXLPKG=libjxl-tools
  if dpkg-query -Wf'${db:Status-abbrev}' "$JXLPKG" 2>/dev/null | grep -q '^i'; then
    echo "The package '$JXLPKG' _is_ already installed!"
  else
    echo "Adding JXL to dependencies"
    RUN_DEPENDENCIES="$RUN_DEPENDENCIES $JXLPKG"
  fi
fi

echo "Installing $RUN_DEPENDENCIES"
sudo apt-get install $RUN_DEPENDENCIES
