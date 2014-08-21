from event import Event
try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule
class Nicklist(BaseModule):
  def post_init(self):
    nicklisting_self_join = Event("__.nicklisting_self_join__")
    nicklisting_other_join = Event("__.nicklisting_other_join__")
    nicklisting_quit = Event("__.nicklisting_quit__")

    nicklisting_self_join.define(message_id=353)
    nicklisting_other_join.define(definition = " JOIN ")
    nicklisting_quit.define(definition = " QUIT ")

    nicklisting_self_join.subscribe(self)
    nicklisting_other_join.subscribe(self)
    nicklisting_quit.subscribe(self)

    # register ourself to our new custom event
    self.bot.register_event(nicklisting_self_join, self)
    self.bot.register_event(nicklisting_other_join, self)
    self.bot.register_event(nicklisting_quit, self)

    self.bot.mem_store['nicklist'] = dict()
    
  def handle(self, event):
    if event.message_id == 353:
      self.bot.mem_store['nicklist'][event.channel] = event.line.split(":")[2].split()


