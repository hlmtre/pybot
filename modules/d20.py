import sys
from random import randint
from event import Event
try:
  if sys.version_info > (3, 0, 0):
    from .basemodule import BaseModule
  else:
    from basemodule import BaseModule
except (ImportError, SystemError):
  from modules.basemodule import BaseModule

class D20(BaseModule):
  def post_init(self):
    d20event = Event("__.d20event__")
    d20event.define(msg_definition="^\.d20")
    d20event.subscribe(self)

    self.help = ".d20 (random number 1-20)"
    # register ourself to our new d20event event
    self.bot.register_event(d20event, self)


  def handle(self, event):
    self.say(event.channel, str(randint(1,20)))
