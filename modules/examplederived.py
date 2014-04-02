from event import Event
try:
  from basemodule import BaseModule
except ImportError:
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
