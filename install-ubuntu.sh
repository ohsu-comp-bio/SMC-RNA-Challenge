#!/bin/bash

sudo apt-get update
sudo apt-get install -y git python-pip python-dev

docker ps
if [ "$?" != "0" ]; then
  sudo apt-get install -y docker.io
  sudo usermod -aG docker $USER
fi

sudo pip install cwltool cwl-runner
sudo pip install synapseclient
git clone https://github.com/Sage-Bionetworks/SMC-RNA-Examples.git

docker pull dreamchallenge/smcrna-functions

