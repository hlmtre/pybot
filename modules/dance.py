##Hold me closer tiny dancer##

from event import Event

try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule

class Dance(BaseModule):

  def post_init(self):
    dance = Event("__.dance__")
    dance.define(msg_definition="^.dance$")
    dance.subscribe(self)
    self.cmd = ".dance"
    self.help = ".dance (bot dances)"
    
    self.bot.register_event(dance, self)
  
  def handle(self, event):
    try:
      self.printer("PRIVMSG " + event.channel + " : :D-\-< " + '\n') #Prints this dancing guy out to proper channel
      self.printer("PRIVMSG " + event.channel + " : :D-|-< " + '\n')
      self.printer("PRIVMSG " + event.channel + " : :D-/-< " + '\n')
    except TypeError:
      pass
