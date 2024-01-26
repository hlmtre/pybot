# Shortener module created by hlmtre#

import sys
import requests
import re

from event import Event
try:
    if sys.version_info > (3, 0, 0):
        from .basemodule import BaseModule
    else:
        from basemodule import BaseModule
except (ImportError, SystemError):
    from modules.basemodule import BaseModule


class Shortener(BaseModule):

    def post_init(self):
        shortener = Event("__urls__")
        # What to look for to trigger event
        shortener.define(msg_definition="https?://[\\S]+")
        shortener.subscribe(self)
        self.r_pattern = r"https?://www.reddit.com/[\S]+|https?://reddit.com/[\S]+|reddit.com/[\S]+|https?://old.reddit.com/[\S]+"
        # register ourself to our new custom event
        self.bot.register_event(shortener, self)

    def handle(self, event):
        try:
            target = re.search("https?://[\\S]+", event.line).group(0)
            url = 'https://u.aql.ink/new'
            payload = target
            if len(target) > 60 and re.match(
                    self.r_pattern, target) is None:  # Post only shortened link if NOT reddit link
                r = requests.post(url, data=payload)
                if re.search("https://u.aql.ink/*", r.text):
                    self.say(event.channel, r.text)
                else:
                    self.bot.debug_print(payload)
                    self.bot.debug_print(r)
                    self.say(event.channel, "Something went wrong :(")
            else:
                return
        except requests.exceptions.HTTPError as e:
            self.bot.debug_print("HTTPError")
            self.bot.debug_print(str(e))

    # Called from the rshort module to shorten the link to put in link
    # description
    def reddit_link(self, link):
        url = 'https://u.aql.ink/new'
        payload = link
        try:
            r = requests.post(url, data=payload)
            if re.search("https://u.aql.ink/*", r.text):
                return r.text
            else:
                return "Something went wrong :("
        except requests.exceptions.HTTPError as e:
            self.bot.debug_print("HTTPError")
            self.bot.debug_print(str(e))
# TODO Try to use code already available instead of using the same code
