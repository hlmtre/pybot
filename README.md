pybot is a python irc bot. he is a project.

he is modular, extensible, multi-threaded, and configurable.


10-second TL;DR:
================

1. modify pybotrc with your channels and passwords.
2. Run `./setup.sh`. It will check for dependencies and create a mysql_init file.
3. `./bot.py pybotrc`
4. rejoice.

Longer explanation:
pybot requires mysqldb. It's probably in your package manager.
It _will_ run without it, it'll just throw lots of exceptions. SQLite integration and no-db (pickle) support are in the works.

Run `./setup.sh` and follow the prompts. It will create a mysql_init file, which you can then run against mysql with `mysql -p < mysql_init`. This will create your database and add a user with full privileges on that database. Your bot will run as this user.
Put that information into the pybotrc.

Run the included mysql_dump file (as root, `mysql -p <pybot's database name> < mysql_dump`).
Add a mysql user for pybot with permissions to update, insert, and delete from the created tables.
Logged into mysql: `grant all on <dbname>.* to '<username>' identified by '<password>';`

Set his dbpass in the config file (pybotrc) to the password you've given him. 
Copy that config file to the home folder of whatever user will be running the bot. (~user/.pybotrc)
As that user, `./bot.py.`


This project uses [smiley's steamapi](https://github.com/smiley/steamapi) for its steam integration, and [PRAW (python reddit API wrapper)](https://praw.readthedocs.org/en/latest/) for the redditinfo module.
