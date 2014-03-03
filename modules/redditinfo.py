try:
  import praw
except ImportError:
  print "WARNING: redditinfo requires praw (https://github.com/praw-dev/praw/)."
  # TODO 

import re
from event import Event
class RedditInfo:
  def __init__(self, events=None, printer_handle=None, bot=None):
    self.events = events
    self.printer = printer_handle
    self.interests = ['__reddit__']
    self.bot = bot

    self.help = None

    reddit = Event("__reddit__")
    reddit.define("https?://www.reddit.com/[\S]+|https?://reddit.com/[\S]+|reddit.com/[\S]+")
    reddit.subscribe(self)

    # this SHOULD replace the need to iterate below and conditionally subscribe...
    self.bot.register_event(reddit, self)

  def handle(self, event):
    print "caught reddit"
    url = re.search("https?://www.reddit.com/[\S]+|https?://reddit.com/[\S]+|reddit.com/[\S]+", event.line).group(0)
    print url
