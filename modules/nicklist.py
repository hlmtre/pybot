import sys
from util import strip_nick
from event import Event
try:
  if sys.version_info > (3, 0, 0):
    from .basemodule import BaseModule
  else:
    from basemodule import BaseModule
except (ImportError, SystemError):
  from modules.basemodule import BaseModule

class Nicklist(BaseModule):
  def post_init(self):
    nicklisting_self_join = Event("__.nicklisting_self_join__")
    nicklisting_other_join = Event("__.nicklisting_other_join__")
    nicklisting_quit = Event("__.nicklisting_quit__")
    nicklisting_part = Event("__.nicklisting_part__")

    nicklisting_command = Event("__.nicklist__")
    nicklisting_command.define(msg_definition="^\.nicklist")

    nicklisting_self_join.define(message_id=353)
    nicklisting_other_join.define(definition="JOIN")
    nicklisting_quit.define(definition="QUIT")
    nicklisting_part.define(definition="PART")

    nicklisting_command.subscribe(self)
    nicklisting_self_join.subscribe(self)
    nicklisting_other_join.subscribe(self)
    nicklisting_quit.subscribe(self)
    nicklisting_part.subscribe(self)

    # register ourself to our new custom event(s)
    self.bot.register_event(nicklisting_self_join, self)
    self.bot.register_event(nicklisting_other_join, self)
    self.bot.register_event(nicklisting_quit, self)
    self.bot.register_event(nicklisting_command,self)
    self.bot.register_event(nicklisting_part,self)

    self.bot.mem_store['nicklist'] = dict()

  def handle(self, event):
    if event.message_id == 353:
      self.bot.mem_store['nicklist'][event.channel] = event.line.split(":")[2].split()
    
    if event.msg.startswith(".nicklist"):
      print(self.bot.mem_store['nicklist'][event.channel])

    if event._type == "__.nicklisting_other_join__":
      try:
        self.bot.mem_store['nicklist'][event.channel].append(strip_nick(event.user))
      except KeyError:
        self.bot.mem_store['nicklist'][event.channel] = list()

    if event._type == "__.nicklisting_part__":
      try:
        self.bot.mem_store['nicklist'][event.channel].remove(strip_nick(event.user))
      except ValueError:
        pass

    if event._type == "__.nicklisting_quit__":
      try:
        for name, chan in self.bot.mem_store['nicklist'].items():
          chan.remove(strip_nick(event.user))
      except ValueError:
        pass
