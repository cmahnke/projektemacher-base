#!/bin/sh
set -eu

RUN_DEPENDENCIES="bash coreutils imagemagick parallel rsync sshpass jq findutils pkg-config poppler-utils	libvips-tools patchelf wget gifsicle libcairo2-dev libpango1.0-dev libgif-dev exiftool xmlstarlet librsvg2-bin"
DOCKER_DEPENDENCIES="moby-buildx moby-cli moby-engine"

sudo apt-get update
if [ "$( . /etc/lsb-release; echo $DISTRIB_RELEASE)" = "22.04" ] ; then
  echo "Marking Docker packages for holding"
  sudo apt-mark hold docker-buildx-plugin docker-ce docker-ce-cli
fi
if [ "$( . /etc/lsb-release; echo $DISTRIB_RELEASE)" = "24.04" ] ; then
  JXLPKG=libjxl-tools
  if dpkg -s "$JXLPKG" >/dev/null 2>&1; then
    echo "'$JXLPKG' ist bereits installiert!"
  else
    echo "Adding JXL to dependencies"
    RUN_DEPENDENCIES="$RUN_DEPENDENCIES $JXLPKG"
  fi
fi

echo "Installing $RUN_DEPENDENCIES"
sudo apt-get install -y $RUN_DEPENDENCIES
