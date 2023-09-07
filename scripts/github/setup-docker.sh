#!/bin/sh

#sudo apt-get update
#if [ "$( . /etc/lsb-release; echo $DISTRIB_RELEASE)" = "22.04" ] ; then
#  echo "Marking Docker packages for holding"
#  for pkg in docker-buildx-plugin docker-ce docker-ce-cli ; do sudo apt-mark hold $pkg; done
#fi

# See https://docs.docker.com/engine/install/ubuntu/
echo "Removing provided Docker version"
sudo apt-get update
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done

echo "Adding Docker key"
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg


echo "Adding package source"
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

echo "Installing Docker"
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker $(id -un)
sudo chgrp -hR docker /run/docker.sock /var/run/docker.sock
