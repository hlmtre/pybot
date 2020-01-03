## Reddit shortener and info ##

import sys
import requests
import re
from event import Event

try:
  import praw
except (ImportError, SystemError):
    print("Warning: rshort module requires praw https://github.com/praw-dev/praw/")
    praw = object
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
    rshort.define(msg_definition="https?://www.reddit.com/[\S]+|https?://reddit.com/[\S]+|reddit.com/[\S]+|https?://old.reddit.com/[\S]+")
    rshort.subscribe(self)
    self.help = None

    # register ourself to our new rshort event
    self.bot.register_event(rshort, self)

  def handle(self, event):
   reddit = praw.Reddit(client_id='ara8VhZCeKcdQw',
                        client_secret='Te_QLIUF1aSh_99ZOzVOCwbgB_s',
                        user_agent="'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'"
                        )
   url = re.search(r"https?://www.reddit.com/[\S]+|https?://reddit.com/[\S]+|reddit.com/[\S]+", event.line).group(0)
   try:
     sub = reddit.submission(url='https://'+url)
     output = '[REDDIT] ' + sub.title + ' | r/' +  sub.subreddit.display_name
      
   except praw.exceptions.ClientException:
     self.say(event.channel, "Fucked link my guy")
   self.say(event.channel, output)



























