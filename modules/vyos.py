from event import Event
try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule
class Vyos(BaseModule):
  def post_init(self):
    vevent = Event("__.vyos__")
    vevent.define(msg_definition="^\.vyos")
    vevent.subscribe(self)

    self.bot.register_event(vevent, self)
  
  def handle(self, event):
    if event.msg.startswith(".vyos") and len(event.msg.split()) > 1:
      self.say(event.channel, "HEY " + event.msg.split()[-1].upper() + " UR VYOS BAWKCXZXCZX IS DOWN")
