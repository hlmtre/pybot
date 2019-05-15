##Shows the URL to the glorious pybot repo##

from event import Event
import re

try:
  from .basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule

class Pimp(BaseModule):

  def post_init(self):
    pimp = Event("__.pimp__")
    pimp.define(msg_definition="^\.pimp$")
    pimp.subscribe(self)
    self.cmd = ".pimp"
    self.help = ".pimp (bot repo URL)"
    
    self.bot.register_event(pimp, self) #Register your event

  def handle(self, event):
    self.say(event.channel, "http://bitbucket.org/hlmtre/pybot") #Just prints that to the intended channel
