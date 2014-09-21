from event import Event
try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule
class KanboModule(BaseModule):
  def post_init(self):
    kanbo = Event("__.custom__")
    kanbo.define(msg_definition="^\.kanbo")
    kanbo.subscribe(self)

    self.bot.register_event(kanbo, self)
    
  def handle(self, event):
    self.say(event.channel, "i am kanbo, watch me disobey simple and direct instruction")
