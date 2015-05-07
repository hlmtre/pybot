#!/bin/bash

if [ "$(id -u)" -ne 0 ]; then
  echo "Error, please execute this script as root."
  exit
fi

user='pybot'
sudo su $user -c ./bot.py
