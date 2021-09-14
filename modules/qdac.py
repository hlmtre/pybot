import random, sys
from pprint import pprint
from event import Event

if sys.version_info > (3, 0, 0):
  try:
    from .basemodule import BaseModule
  except (ImportError, SystemError):
    from modules.basemodule import BaseModule
else:
  try:
      from basemodule import BaseModule
  except (ImportError, SystemError):
    from modules.basemodule import BaseModule

class Qdac(BaseModule):
  def post_init(self):
    qdac = Event("__.qdac__")
    qdac.define(msg_definition="^\.qdac")
    qdac.subscribe(self)
    self.help = ".qdac <trigger> <action to take: [say]> <thing to say>"

    # register ourself to our new qdac event
    self.bot.register_event(qdac, self)

  def handle(self, event):
    words = event.msg.split(" ", maxsplit=3)
    if not len(words) == 4:
      self.say(event.channel, "qdac: invalid command format")
      return

    def qdac_handle(event):
      print("QDAC_HANDLE CALLED")
      print(event.msg)
      print("ASLDKAJSLDK")
      if event.msg.startswith(self.trigger):
        self.action(event.channel, 'SOMETHING')

    trigger, action, output = words[1], words[2], words[3]
    new_event = Event("__" + trigger + "__")
    new_event.define(msg_definition="^\\" + trigger)
    action = self.say
    new_module = type(trigger.strip(".").upper(), (BaseModule,),  {"handle": qdac_handle, "trigger": trigger, "action": action})
    new_event.subscribe(new_module)
    print(new_event.subscribers[0].trigger)
    self.bot.register_event(new_event, new_module)
    self.say(event.channel, "command added")
