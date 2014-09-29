#!/bin/bash

if [ "$(id -u)" -ne 0 ]; then
  echo "Error, please execute this script as root."
  exit
fi

sudo aptitude install -y python-pip python2.7 python2.7-dev libmysqlclient-dev
sudo pip install -r requirements.txt
