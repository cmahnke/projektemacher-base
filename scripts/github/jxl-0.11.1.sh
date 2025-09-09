#!/bin/sh

# See also https://doc.owncloud.com/server/next/admin_manual/installation/manual_installation/manual_imagick7.html

if test -z "`which sudo`" ; then
  apt-get update
  apt-get install -y sudo wget
fi

# This needs the `software-properties-common` package
#sudo add-apt-repository -y universe
#sudo apt-get update
sudo apt-get install -y libstdc++6 libtcmalloc-minimal4 libgcc-s1 libc6 libilmbase25 libopenexr25 libhwy0 libhwy-dev libpng16-16 libbrotli1 libjpeg8 libgif7

mkdir -p /tmp/jxl
cd /tmp/jxl

wget https://github.com/libjxl/libjxl/releases/download/v0.11.1/jxl-debs-amd64-ubuntu-24.04-v0.11.1.tar.gz
tar xzf jxl-debs-amd64-ubuntu-24.04-v0.11.1.tar.gz

sudo apt install -y -f ./libjxl_0.11.1_amd64.deb
sudo apt install -y -f ./jxl_0.11.1_amd64.deb
sudo apt install -y -f ./libjxl-dev_0.11.1_amd64.deb

cd ..
rm -rf jxl
