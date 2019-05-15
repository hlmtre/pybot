##Lists modules and usage##

from event import Event
import sys
try:
  if sys.version_info > (3,0,0):
    from .basemodule import BaseModule
  else:
    from basemodule import BaseModule
except (ImportError, SystemError):
  from modules.basemodule import BaseModule

class Help(BaseModule):
  def post_init(self):
    help = Event("__.help__")
    help.define(msg_definition="^\.help")
    help.subscribe(self)
    self.cmd = ".help"
    
    # register ourself to our new custom event
    self.bot.register_event(help, self)
  
  def handle(self, event):
    try:
      my_modules = list()
      for m in self.bot.events_list:
        for s in m.subscribers:
          my_modules.append(s)

      modules_set = set(my_modules)
      line_list = list()

      for sm in modules_set:
        if hasattr(sm, "help") and sm.help is not None:
          line_list.append(sm.help)
      
      """
      This jenky block controls how many modules to print per line
      To change the amount of modules print per line change the first 'q' to whatever number and match the incremented 'q and f' to the same number
      """
      #TODO make it better, probably pull out into a function
      self.say(event.user, "Help: \n")
      q = 3 # sets the starting end index
      f = 0 # sets the index to start from (The beginning of the list usually)
      for h in range(len(line_list)):
        self.say(event.user, ", ".join(line_list[f:q])) # Prints the line in a private message for each slice
        q += 3 # increments the end index
        f += 3 # increments the start index
        if q >= len(line_list):
          break
    except:
      pass

