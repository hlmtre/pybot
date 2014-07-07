#!/bin/bash
#
# This script will bootstrap a local Ubuntu system, installing dependencies and preparing it for
# pybot development.

if [ "$(id -u)" -ne 0 ]; then
  echo "Error, please execute this script as root."
  exit
else
  echo "Bootstrapping system..."
  apt-get update
  debconf-set-selections <<< 'mysql-server mysql-server/root_password       password root'
  debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password root'
  apt-get -qy install python-pip python2.7 python2.7-dev mysql-server mysql-client libmysqlclient-dev
  pip install -r /vagrant/requirements.txt
  echo "Bootstrap finished!"
  echo
  echo "Please note, mysql was installed with a default root password of 'root'."
  echo "You really should change this password immediately."
  echo "To do this, please run the following command and follow the prompts: "
  echo
  echo "sudo mysqladmin -u root -p password"
  echo
  exit
fi
