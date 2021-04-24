#!/bin/sh
RUN_DEPENDENCIES="imagemagick parallel rsync sshpass bash jq findutils"

echo "Installing $RUN_DEPENDENCIES"
sudo apt-get install $RUN_DEPENDENCIES

# We currently use Ububtu 18.04 which ships an quit old python version - this is thew reason why we use the GitHub Python action
#python -m pip install --upgrade pip
#pip install pillow termcolor
