[![Build Status](https://travis-ci.org/hlmtre/pybot.svg?branch=master)](https://travis-ci.org/hlmtre/pybot)
[![Documentation Status](https://readthedocs.org/projects/pybot/badge/?version=master)](https://pybot.readthedocs.io/en/master/?badge=master)
![Github action build status](https://github.com/hlmtre/pybot/workflows/Python%20application/badge.svg)
[![Scrutinizer coverage](https://scrutinizer-ci.com/g/hlmtre/pybot/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/hlmtre/pybot/?branch=master)

[ReadTheDocs documentation](http://pybot.readthedocs.org/en/master/ "ReadTheDocs pybot documentation")

pybot is a python irc bot. he is a project.
-------------------------------------------

he is modular, extensible, multi-threaded (for network independence!), and configurable.

pybot runs on python 2.7 and >3.5, on both windows and linux, though current development is all geared towards >3.5.

**master branch should be stable. feature branches can be broken at any time.**

If You've Got Docker
====================

This is mucho easier-o. Just
----------------------------

    docker build . -t pybox
    docker run -it pybox --nick <botnick> --server <yourserver> --port 6667 --channels "#c1, #c2" --owner <yournick>

(Now probably more than) 10-second TL;DR:
=========================================

Take care of dependencies. If you don't use MySQL and don't care about certain modules breaking, you don't need anything but python 2.7/3.5 and standard libs.
-----------------------------------------------------------------------------------------------------------------------------------------------------
    python -m venv pybot-venv
    source pybot-venv/bin/activate
    # so as to not stuff pips everywhere
    pip install -r requirements.txt

* python-dev
* libmysqlclient-dev (aka mysql-python in pip)
* requests (used in a variety of modules)
* praw (for reddit info module)
* mysql-python (if you do use mysql)
* sphinx (for docs)
* python-twitter (twitterposter)
* pytz (tzone)

Local Development (with sqlite3)
--------------------------------
1. Copy pybotrc to the user who will run the bot *(you can probably do `cp pybotrc ~/.pybotrc`)*
2. Modify ~/.pybotrc with your network, owner, and nickname.
3. `./pybot.py`
4. laugh at mysql guys.
5. continue laughing.
6. for debugging purposes, `./pybot.py -d.`

Local Development (with MySQL)
------------------------------
1. modify pybotrc with your channels and passwords.
2. run `sudo ./bootstrap.sh` to install pybot dependencies such as mysql.
3. run `./setup.sh`. It will check for module dependencies and create a mysql\_init file. `mysql -p < mysql\_init`
4. `./pybot.py pybotrc`
5. rejoice.
6. for debugging purposes, `./pybot.py -d.`

Manual
------
Add a mysql user for pybot with permissions to update, insert, and delete from the created tables.
Logged into mysql: `grant all on <dbname>.* to '<username>' identified by '<password>';`

Run the included mysql\_dump file (as root, `mysql -p <pybot's database name> < mysql\_dump`).
Set his dbpass in the config file (pybotrc) to the password you've given him.
Copy that config file to the home folder of whatever user will be running the bot. (~user/.pybotrc)
As that user, `./pybot.py.`

Vagrant Development
-------------------
If you have Vagrant locally installed and configured, you can set up pybot by invoking
`vagrant up`. Your development environment will be configured, and you can skip step 1 and
2 above. After that, SSH into your VM and do steps 3 through 5 to finish things off.

Images & Explanation
====================

![debug mode](http://i.imgur.com/x99zXOJ.png "debug mode")

Here pybot is connected to two networks at once. They are held entirely separately. Modules loaded on one are independent of modules loaded on another.
If one server goes down, the other connections to other networks are unaffected.

![youtube module](http://i.imgur.com/kUYW3e5.png "youtube module")

![a totally not contrived example](http://i.imgur.com/jMpkjRf.png "a totally not contrived example")

TODO
----
* add birthday module (save birthdays for your channel regulars!)
* update scheduler to accept *at* commands - .schedule at 5pm say #development pick your child from daycare
