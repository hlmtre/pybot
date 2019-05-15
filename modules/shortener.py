#Shortener module created by hlmtre#

import requests
import re

from event import Event
try:
  from .basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule
class Shortener(BaseModule):
  
  def post_init(self):
    shortener = Event("__urls__")
    shortener.define(msg_definition = "https?://[\S]+") # What to look for to trigger event
    shortener.subscribe(self)

    # register ourself to our new custom event
    self.bot.register_event(shortener, self)
    
  def handle(self, event):
    try:
      target = re.search("https?://[\S]+", event.line).group(0)
      if len(target) > 60:
        url = 'https://is.gd/create.php'
        payload = {'format':'simple', 'url':target}
        r = requests.get(url, params=payload)
        self.say(event.channel, r.text)
    except requests.exceptions.HTTPError as e:
      self.bot.debug_print("HTTPError")
      self.bot.debug_print(str(e))
