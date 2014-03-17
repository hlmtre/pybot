from event import Event
from basemodule import BaseModule
class Test(BaseModule):
  def post_init(self):
    custom = Event("__.custom__")
    custom.define(msg_definition="^\.custom")
    custom.subscribe(self)

    # register ourself to our new custom event
    self.bot.register_event(custom, self)
    
  def handle(self, event):
    self.say(event.channel, "custom event caught!")
