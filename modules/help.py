from time import sleep
from event import Event
class Help:
  def __init__(self, events=None, printer_handle=None, bot=None, say=None):
    self.events = events
    self.printer = printer_handle
    self.interests = ['__.help__']
    self.bot = bot

    for event in events:
      if event._type in self.interests:
        event.subscribe(self)

    help = Event("__.help__")
    help.define(msg_definition="^\.help")
    help.subscribe(self)
    self.bot.register_event(help)

    self.help = ".help"

  def handle(self, event):
    try:
      my_modules = list()
      self.printer("PRIVMSG " + event.user + " :Help: \n")
      for m in self.bot.events_list:
        for s in m.subscribers:
          my_modules.append(s)

      modules_set = set(my_modules)
      line_list = list()
      for sm in modules_set:
        if hasattr(sm, "help") and sm.help is not None:
          line_list.append(sm.help)

      self.printer("PRIVMSG " + event.user + " :" + ", ".join(line_list) + "\n")

    except:
      pass
