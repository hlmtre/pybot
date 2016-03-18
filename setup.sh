#!/bin/bash
echo "Checking dependencies..."
python -c "
try:
  import praw
except ImportError:
  print 'redditmodule requires praw. pybot will run fine without it.'
try:
  import MySQLdb
except ImportError:
  print 'pybot requires mysqldb. It will run without it; it\'ll just throw lots of errors.'
try:
  import requests
except ImportError:
  print 'several modules require requests. pybot will run, but several modules will not function.'
"
if [[ $? -ne 0 ]]; then
  echo "Dependency checks failed.
  pybot's module dependencies are available in pip, which is probably available in your package manager.
  Install dependencies with 'pip install <package name>'."
else
  echo "Dependency checks succeeded."
fi

read -p "Do you want to use mysql? [y/n] " mysql_answer
if [[ $mysql_answer == "y" ]]; then
  echo "The following information should be what is in your pybotrc file, for dbname, dbusername, and dbpass, respectively."
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

  echo "mysql_init file has been created. As root or otherwise mysql-privileged user, run 'mysql -p < mysql_init'"
else
  echo "you're using sqlite. you're done!"
fi
