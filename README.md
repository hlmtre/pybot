[![Build Status](http://ci.zero9f9.com/job/pybot/badge/icon)](http://ci.zero9f9.com/job/pybot/)
pybot is a python irc bot. he is a project.

he is modular, extensible, multi-threaded, and configurable.

pybot runs on python 2.6 and 2.7 (though steamapi does not work with 2.6, the core bot does).
python versions > 3 are in the works.


10-second TL;DR:
================

Local Development
-----------------
1. modify pybotrc with your channels and passwords.
2. run `sudo ./bootstrap.sh` to install pybot dependencies such as mysql.
3. run `./setup.sh`. It will check for module dependencies and create a mysql_init file.
4. `./bot.py pybotrc`
5. rejoice.


6. for debugging purposes, `./bot.py -d.`

Vagrant Development
-------------------
If you have Vagrant locally installed and configured, you can set up pybot by invoking
`vagrant up`. Your development environment will be configured, and you can skip step 1 and
2 above. After that, SSH into your VM and do steps 3 through 5 to finish things off.

Environment Dependencies
------------------------
pybot requires mysqldb. It's probably in your package manager.
It _will_ run without it, it'll just throw lots of exceptions. SQLite integration and
no-db (pickle) support are in the works.

Automagic
---------
Run `./bootstrap.sh` and wait for your system to be configured. Mysql will be installed with a
default password of 'root', which you'll definitely want to change.

Run `./setup.sh` and follow the prompts. It will create a mysql_init file, which you can then
run against mysql with `mysql -p < mysql_init`. This will create your database and add a user
with full privileges on that database. Your bot will run as this user.

Put that information into the pybotrc.
If you do not run `./setup.sh` you will have to perform the step below.
___
Manual
------
Add a mysql user for pybot with permissions to update, insert, and delete from the created tables.
Logged into mysql: `grant all on <dbname>.* to '<username>' identified by '<password>';`
___

Run the included mysql_dump file (as root, `mysql -p <pybot's database name> < mysql_dump`).
Set his dbpass in the config file (pybotrc) to the password you've given him.
Copy that config file to the home folder of whatever user will be running the bot. (~user/.pybotrc)
As that user, `./bot.py.`

Images & Explanation
====================

![debug mode](http://i.imgur.com/k5T7SKq.png "debug mode")

Here pybot is connected to two networks at once. They are held entirely separately. Modules loaded on one are independent of modules loaded on another.
If one server goes down, the other connections to other networks are unaffected.

![youtube module](http://i.imgur.com/kUYW3e5.png "youtube module")

![a totally not contrived example](http://i.imgur.com/jMpkjRf.png "a totally not contrived example")


This project uses [smiley's steamapi](https://github.com/smiley/steamapi) for its steam integration, and
[PRAW (python reddit API wrapper)](https://praw.readthedocs.org/en/latest/) for the redditinfo module.
