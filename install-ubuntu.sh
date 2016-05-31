#!/bin/bash


sudo apt-get install -y python-pip python-dev

docker ps
if [ "$?" != "0" ]; then
  sudo apt-get install docker.io
  sudo usermod -aG docker $USER
fi

sudo pip install cwltool
git clone https://github.com/Sage-Bionetworks/SMC-RNA-Examples.git

docker pull dreamchallenge/smcrna-functions

