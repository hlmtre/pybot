#!/bin/bash

echo "The following information should be what are in your pybotrc file, for dbname, dbusername, and dbpass, respectively."
echo
read -p "Enter database name for bot to use: " dbname
read -p "Enter MYSQL username bot will log in with: " username
read -s -p "Enter user password: " password
echo
read -s -p "Re-enter password: " password2
echo

if [ -f mysql_init ]; then
  rm mysql_init
fi
echo "CREATE DATABASE IF NOT EXISTS $dbname;" > mysql_init
echo "GRANT ALL ON $dbname.* TO '$username'@'localhost' IDENTIFIED BY '$password';" >> mysql_init

echo "mysql_init file has been created. As root or otherwise mysql-privileged user, run mysql -p < mysql_init"
