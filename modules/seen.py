from event import Event
from util import __prettyDate as prettydate
from datetime import datetime

class UserHistory():
  def __init__(self, user=None, timestamp=None):
    self.user = user
    self.timestamp = timestamp

try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule

class Seen(BaseModule):
  def mem_store_init(self):
    if not "tell" in self.bot.mem_store:
      self.bot.mem_store['tell'] = dict()

  def post_init(self):
    self.interests = ['__privmsg__']  # should be first event in the listing.. so lines being added is a priority
    for event in self.events:
      if event._type in self.interests:
        event.subscribe(self)

    self.help = ".seen <nickname>. describes when the bot last saw <nickname> active in channel"  

    self.mem_store_init()
    
  def handle(self, event):
    self.mem_store_init()

    if event.msg.startswith(".seen"):
      try:
        nick = event.msg.split()[1]
      except IndexError:
        return
      if nick in self.bot.mem_store['tell']:
        self.say(event.channel, "Last saw " + nick + " " + prettydate(self.bot.mem_store['tell'][nick]))
      else:
        self.say(event.channel, "haven't seen " + nick)

    self.bot.mem_store['tell'][event.user] = datetime.now()

