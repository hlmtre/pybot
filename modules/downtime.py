import time
from datetime import datetime, timedelta
from event import Event
import random
try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule

class Downtime(BaseModule):
  def post_init(self):
    downtime_event = Event("__.downtime__")
    downtime_event.define(msg_definition="^\.downtime")
    downtime_event.subscribe(self)

    # register ourself to our new custom event
    self.bot.register_event(downtime_event, self)

    self.drinks = ['a beer', 'a scotch', 'a bloody mary', 'a nice glass of wine', 'FUCKIN FOUR LOKO', 'a crisp cider']
    
    self.action_string = "\001ACTION "
    
  def handle(self, event):
    self._downtime(event)

  def _downtime(self, event):
    if event.user.lower() == "george" or "thorogood" in event.user.lower():
      self.say(event.channel, self.action_string + ' gets ' + event.user + ' one bourbon, one scotch, one beer'+ "\001\n")
    else:
      self.say(event.channel, self.action_string + ' gets ' + event.user + ' ' + random.choice(self.drinks)+ "\001\n")

