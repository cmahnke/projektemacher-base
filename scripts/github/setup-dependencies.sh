#!/bin/sh
RUN_DEPENDENCIES="bash coreutils imagemagick parallel rsync sshpass bash jq findutils libcairo2-dev pkg-config poppler-utils	libvips-tools patchelf wget yarn"
DOCKER_DEPENDENCIES="moby-buildx moby-cli moby-engine"

sudo apt-get update
if [ "$( . /etc/lsb-release; echo $DISTRIB_RELEASE)" = "22.04" ] ; then
  echo "Marking Docker packages for holding"
  for pkg in docker-buildx-plugin docker-ce docker-ce-cli ; do sudo apt-mark hold $pkg; done
fi
echo "Installing $RUN_DEPENDENCIES"
sudo apt-get install $RUN_DEPENDENCIES
