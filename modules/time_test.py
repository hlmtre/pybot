from event import Event
try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule
class TimeTest(BaseModule):
  def post_init(self):
    self.interests = ["__time_test__"]
    self.time_delta = 20
    """
      the time_event will increment this each time it's called, unless we call handle on it. then it's set to 0, to restart the process. how zen.
    """
    self.time_since = 0 # initialize our time since to zero. 
    for event in self.events:
      if event._type in self.interests:
        event.subscribe(self)
    #custom = Event("__.custom__")
    #custom.define(msg_definition="^\.custom")
    #custom.subscribe(self)

    # register ourself to our new custom event
    #self.bot.register_event(custom, self)
    
  def handle(self, event):
    for channel in self.bot.chan_list:
      self.say(channel, "called every twenty seconds, and this is one of 'em")
    #self.say(event.channel, "custom event caught!")
