import requests
from . import version
try:
  import praw
  successful_import = True
except (ImportError, SystemError):
  print("WARNING: redditinfo requires praw (https://github.com/praw-dev/praw/, or pip install praw).")
  successful_import = False

if successful_import is True:
  import re
  from event import Event
  class RedditInfo:
    def __init__(self, events=None, printer_handle=None, bot=None, say=None):
      self.events = events
      self.printer = printer_handle
      self.interests = ['__reddit__']
      self.bot = bot
      self.say = say

      self.user_agent = 'pybot ' + version.__version__ + ' by /u/hlmtre; http://bitbucket.org/hlmtre/pybot'

      self.help = None

      reddit = Event("__reddit__")
      reddit.define("https?://www.reddit.com/[\S]+|https?://reddit.com/[\S]+|reddit.com/[\S]+")
      reddit.subscribe(self)

      self.bot.register_event(reddit, self)

    def handle(self, event):
      url = re.search("https?://www.reddit.com/[\S]+|https?://reddit.com/[\S]+|reddit.com/[\S]+", event.line).group(0)
      me = praw.Reddit(self.user_agent)
      try:
        s = me.get_submission(url)
      except requests.exceptions.MissingSchema:
        s = me.get_submission('http://'+url)
      except TypeError:
        return
      message = '[REDDIT] ' + s.title
      if s.is_self:
          message = message + ' (self.' + s.subreddit.display_name + ')'
      else:
          message = message + ' to r/' + s.subreddit.display_name
      if s.over_18:
          message = message + ' 05[NSFW]'
          #TODO implement per-channel settings db, and make this able to kick
      if s.author:
          author = s.author.name
      else:
          author = '[deleted]'
      message = (message + ' | ' + author)
      #TODO add creation time with s.created
      self.printer("PRIVMSG " + event.channel + " :" + message + "\n")
