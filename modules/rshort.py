## Reddit link information ##

import version
successful_import = False
try:  # Checks to make sure praw has everything it needs before importing the rest of the module
    import praw
    try:
        reddit = praw.Reddit(
            'pybot',
            user_agent='pybot ' +
            version.__version__ +
            ' by /u/hlmtre; https://github.com/hlmtre/pybot')
        successful_import = True
    except BaseException:
        pass
except (ImportError, SystemError):
    print("Warning: rshort module requires praw https://github.com/praw-dev/praw/")
except praw.exceptions.ClientException:
    print('Warning: rshort requires the "praw.ini" file in the top pybot directory\
  to be filled in with the client_id and client_secret.')
    successful_import = False

if successful_import:
    import sys
    import requests
    import re
    from shortener import Shortener
    from datetime import datetime
    from event import Event

    if sys.version_info > (3, 0, 0):
        try:
            from .basemodule import BaseModule
        except (ImportError, SystemError):
            from modules.basemodule import BaseModule
    else:
        try:
            from basemodule import BaseModule
        except (ImportError, SystemError):
            from modules.basemodule import BaseModule

    class Rshort(BaseModule):

        def post_init(self):
            rshort = Event("__rshort__")
            rshort.define(
                msg_definition="https?://www.reddit.com/[\\S]+|https?://reddit.com/[\\S]+|reddit.com/[\\S]+|https?://old.reddit.com/[\\S]+")
            rshort.subscribe(self)
            self.help = None
            self.r_pattern = r"https?://www.reddit.com/[\S]+|https?://reddit.com/[\S]+|reddit.com/[\S]+|https?://old.reddit.com/[\S]+"
            # register ourself to our new rshort event
            self.bot.register_event(rshort, self)

        def handle(self, event):

            url = re.search(self.r_pattern, event.line).group(0)
            try:
                sub = reddit.submission(url='https://' + url)
            except praw.exceptions.ClientException:  # If the link is broken we should not do anything at all
                return
            sub_time = datetime.utcfromtimestamp(sub.created).strftime(
                '%Y/%m/%d@%H:%M')  # converts from POSIX timestamp to human readable
            message = '[REDDIT] ' + sub.title
            if sub.is_self:
                message = message + \
                    ' (self.' + sub.subreddit.display_name + ')'
            else:
                message = message + ' to r/' + sub.subreddit.display_name
            if sub.author:
                author = 'u/' + sub.author.name
            else:
                author = '[deleted]'
            if sub.over_18:
                message = message + ' 05[NSFW]'
                # TODO implement per-channel settings db, and make this able to
                # kick
            message = (message + ' | ' + author + ' | ' + sub_time)
            self.say(
                event.channel,
                message +
                ' | ' +
                Shortener.reddit_link(
                    self,
                    url))
