[![Build Status](https://ci.zero9f9.com/job/pybot/badge/icon)](https://ci.zero9f9.com/job/pybot/)

[ReadTheDocs documentation](http://pybot.readthedocs.org/en/master/ "ReadTheDocs pybot documentation")

pybot is a python irc bot. he is a project.
-------------------------------------------

he is modular, extensible, multi-threaded, and configurable.

pybot runs on python 2.6 and 2.7, on both windows and linux.
python versions > 3 are in the works.


(Now probably more than) 10-second TL;DR:
=========================================

Take care of dependencies. If you don't use MySQL and don't care about twitter posting or reddit info, you don't need anything but python 2.6 or 2.7 and standard libs.
-----------------------------------------------------------------------------------------------------------------------------------------------------
* python-dev
* libmysqlclient-dev (aka mysql-python in pip)
* requests
* praw (for reddit info module)
* mysql-python (if you do use mysql)
* sphinx (for docs)
* python-twitter (twitterposter)

Local Development (with sqlite3)
--------------------------------
1. Copy pybotrc to the user who will run the bot (you can probably do `cp pybotrc ~/.pybotrc`)
2. Modify ~/.pybotrc with your network, owner, and nickname.
3. `./bot.py`
4. laugh at mysql guys.
5. continue laughing.
6. for debugging purposes, `./bot.py -d.`

Local Development (with MySQL)
------------------------------
1. modify pybotrc with your channels and passwords.
2. run `sudo ./bootstrap.sh` to install pybot dependencies such as mysql.
3. run `./setup.sh`. It will check for module dependencies and create a mysql_init file. `mysql -p < mysql_init`
4. `./bot.py pybotrc`
5. rejoice.
6. for debugging purposes, `./bot.py -d.`

Manual
------
Add a mysql user for pybot with permissions to update, insert, and delete from the created tables.
Logged into mysql: `grant all on <dbname>.* to '<username>' identified by '<password>';`
___

Run the included mysql_dump file (as root, `mysql -p <pybot's database name> < mysql_dump`).
Set his dbpass in the config file (pybotrc) to the password you've given him.
Copy that config file to the home folder of whatever user will be running the bot. (~user/.pybotrc)
As that user, `./bot.py.`

Vagrant Development
-------------------
If you have Vagrant locally installed and configured, you can set up pybot by invoking
`vagrant up`. Your development environment will be configured, and you can skip step 1 and
2 above. After that, SSH into your VM and do steps 3 through 5 to finish things off.

Images & Explanation
====================

![debug mode](http://i.imgur.com/k5T7SKq.png "debug mode")

Here pybot is connected to two networks at once. They are held entirely separately. Modules loaded on one are independent of modules loaded on another.
If one server goes down, the other connections to other networks are unaffected.

![youtube module](http://i.imgur.com/kUYW3e5.png "youtube module")

![a totally not contrived example](http://i.imgur.com/jMpkjRf.png "a totally not contrived example")