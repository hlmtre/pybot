from random import randint
from event import Event
try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule
class D20(BaseModule):
  def post_init(self):
    d20event = Event("__.d20event__")
    d20event.define(msg_definition="^\.d20")
    d20event.subscribe(self)

    # register ourself to our new d20event event
    self.bot.register_event(d20event, self)
    

  def handle(self, event):
    self.say(event.channel, str(randint(1,20)))
