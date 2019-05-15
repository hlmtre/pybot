#Prints to your Console when disconnected#

from event import Event
try:
  from .basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule
class Disconnect_Yeller(BaseModule):
  def post_init(self):
    self.interests = ['__.disconnection__']

    for event in self.events:
      if event._type in self.interests:
        event.subscribe(self)

  def handle(self, event):
    print("I'VE BEEN DISCONNECTED")
    print("OH COCK")
