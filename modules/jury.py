from event import Event
import random
try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule
class Jury(BaseModule):
  def post_init(self):
    jury = Event("__.jury__")
    jury.define(msg_definition="^\.jury")
    jury.subscribe(self)

    # register ourself to our new jury event
    self.bot.register_event(jury, self)
    
  def handle(self, event):
    if event.msg.startswith(".jury"):
      votes = 0
      for i in range(12):
        votes = votes + int(random.choice("01"))
      self.say(event.channel, "Twelve jurors, " + str(votes) + " yeas and " + str((12-votes)) + " nays.")
