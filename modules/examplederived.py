import sys
from event import Event
try:
  if sys.version_info > (3, 0, 0):
    from .basemodule import BaseModule
  else:
    from basemodule import BaseModule
except (ImportError, SystemError):
  from modules.basemodule import BaseModule

class ExampleDerived(BaseModule):
  def post_init(self):
    pass
    #custom = Event("__.custom__")
    #custom.define(msg_definition="^\.custom")
    #custom.subscribe(self)

    # register ourself to our new custom event
    #self.bot.register_event(custom, self)

  def handle(self, event):
    pass
    #self.say(event.channel, "custom event caught!")
