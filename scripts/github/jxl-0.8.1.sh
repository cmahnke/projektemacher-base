#!/bin/sh

# See also https://doc.owncloud.com/server/next/admin_manual/installation/manual_installation/manual_imagick7.html

sudo add-apt-repository universe
sudo apt-get install libilmbase25 libopenexr25 libtcmalloc-minimal4 libhwy-dev

mkdir -p /tmp/jxl
cd /tmp/jxl

wget https://github.com/libjxl/libjxl/releases/download/v0.8.1/jxl-debs-amd64-ubuntu-20.04-v0.8.1.tar.gz
tar xzf jxl-debs-amd64-ubuntu-20.04-v0.8.1.tar.gz


sudo apt install -f ./libjxl_0.8.1_amd64.deb
sudo apt install -f ./jxl_0.8.1_amd64.deb
sudo apt install -f ./libjxl-dev_0.8.1_amd64.deb

cd ..
rm -rf jxl
