#!/bin/bash
# This script is useful if you want to run pybot as his own user.
# Either add a pybot user to your system `adduser pybot`, or
# change the user here to who you want to run the bot.
# Or you can run the bot as yourself. Whatever. See if I care.
user='pybot'

if [ "$(id -u)" -ne 0 ]; then
  echo "Error, please execute this script as root."
  exit
fi

sudo su $user -c ./pybot.py
