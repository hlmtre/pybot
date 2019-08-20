import sys
from event import Event
from util import __prettyDate as prettydate
from util import strip_nick
from datetime import datetime

try:
  if sys.version_info > (3, 0, 0):
    from .basemodule import BaseModule
  else:
    from basemodule import BaseModule
except (ImportError, SystemError):
  from modules.basemodule import BaseModule

class Seen(BaseModule):
  def mem_store_init(self):
    if not "seen" in self.bot.mem_store:
      self.bot.mem_store['seen'] = dict()

  def post_init(self):
    self.interests = ['__privmsg__']  # should be first event in the listing.. so lines being added is a priority
    for event in self.events:
      if event._type in self.interests:
        event.subscribe(self)

    self.help = ".seen <nickname>. describes when the bot last saw <nickname> active on server"

    self.mem_store_init()

  def handle(self, event):
    self.mem_store_init()

    if event.msg.startswith(".seen"):
      try:
        nick = strip_nick(event.msg.split()[1].lower()) # store all nicks in lowercase
      except IndexError:
        return
      if nick in (n.lower() for n in self.bot.mem_store['seen']):
        self.say(event.channel, "Last saw " + nick + " " + prettydate(self.bot.mem_store['seen'][nick]))
      else:
        self.say(event.channel, "haven't seen " + nick)

    self.bot.mem_store['seen'][strip_nick(event.user).lower()] = datetime.now()

