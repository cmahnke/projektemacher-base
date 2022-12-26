#!/bin/sh

sudo add-apt-repository universe
sudo apt-get install libilmbase24 libopenexr24 libtcmalloc-minimal4 libhwy-dev

mkdir -p /tmp/jxl
cd /tmp/jxl

wget https://github.com/libjxl/libjxl/releases/download/v0.7.0/jxl-debs-amd64-ubuntu-20.04-v0.7.0.tar.gz
tar xzf jxl-debs-amd64-ubuntu-20.04-v0.7.0.tar.gz


sudo apt install -f ./libjxl_0.7_amd64.deb
sudo apt install -f ./jxl_0.7_amd64.deb
sudo apt install -f ./libjxl-dev_0.7_amd64.deb

cd ..
rm -rf jxl
