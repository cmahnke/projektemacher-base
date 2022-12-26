#!/bin/sh

mkdir -p /tmp/jxl
cd /tmp/jxl

wget https://github.com/libjxl/libjxl/releases/download/v0.7.0/jxl-debs-amd64-ubuntu-20.04-v0.7.0.tar.gz
tar xzf jxl-debs-amd64-ubuntu-20.04-v0.7.0.tar.gz


sudo dpkg -i libjxl_0.7_amd64.deb
sudo dpkg -i jxl_0.7_amd64.deb
sudo dpkg -i libjxl-dev_0.7_amd64.deb

cd ..
rm -rf jxl
