#!/bin/bash

# setup pip
apt-get update 
apt-get install -y python-dev
apt-get install -y python-pip

# install storm ssh dependencies
pip install -e /vagrant

# setup pth file
echo /vagrant > /usr/local/lib/python2.7/dist-packages/storm.pth

# add ssh entries
storm add google google.com
storm add yahoo yahoo.com




