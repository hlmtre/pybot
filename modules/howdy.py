from event import Event
import random
try:
  from .basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule
class Howdy(BaseModule):
  def post_init(self):
    howdy = Event("__.howdy__")
    howdy.define(msg_definition="^\.howdy")
    howdy.subscribe(self)
    self.help = ".howdy (spits out cowboy stuff)"

    # register ourself to our new howdy event
    self.bot.register_event(howdy, self)
    
  def handle(self, event):
    self.say(event.channel, "https://i.imgur.com/veDWwOv.gif")
