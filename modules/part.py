#Part module, removes bot from specified channel#

from event import Event
try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule
class Part(BaseModule):
  """This command should be used as a private message to the bot or else it will not work"""
  def post_init(self):
    part = Event("__.part__")
    part.define(msg_definition="^\.part")
    part.subscribe(self)
    self.help = ".part <channel> 'use as pm to the bot'"
    
    # register ourself to our new custom event
    self.bot.register_event(part, self)

  def handle(self, event):
    try:
      if self.bot.conf.getOwner(self.bot.network) == event.line.split()[0].split("!",1)[0].replace(":","") and event.line.split()[2] == self.bot.conf.getNick(self.bot.network):
        self.bot.send("PART " + event.line.split()[4] + '\n')
    except:
      pass

