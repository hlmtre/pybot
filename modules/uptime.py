from event import Event
try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule
class Uptime(BaseModule):
  def post_init(self):
    uptime_event = Event("__.uptime__")
    uptime_event.define(msg_definition="^\.uptime")
    uptime_event.subscribe(self)

    # register ourself to our new custom event
    self.bot.register_event(uptime_event, self)
    
  def handle(self, event):
    self.bot.brain._uptime(event.channel)
