try:
  import praw
  successful_import = True
except ImportError:
  print "WARNING: redditinfo requires praw (https://github.com/praw-dev/praw/)."
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

      self.user_agent = 'pybot 0.6.4 by /u/hlmtre; http://bits.zero9f9.com/pybot'

      self.help = None

      reddit = Event("__reddit__")
      reddit.define("https?://www.reddit.com/[\S]+|https?://reddit.com/[\S]+|reddit.com/[\S]+")
      reddit.subscribe(self)

      # this SHOULD replace the need to iterate below and conditionally subscribe...
      self.bot.register_event(reddit, self)

    def handle(self, event):
      url = re.search("https?://www.reddit.com/[\S]+|https?://reddit.com/[\S]+|reddit.com/[\S]+", event.line).group(0)
      me = praw.Reddit(self.user_agent)
      s = me.get_submission(url)
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
      message = (message + ' | ' + str(s.ups - s.downs) + ' points (03'
                 + str(s.ups) + '|05' + str(s.downs) + ') | ' + author)
      #TODO add creation time with s.created
      self.printer("PRIVMSG " + event.channel + " :" + message + "\n")
