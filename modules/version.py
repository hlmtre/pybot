import version
from event import Event
try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule
class Version(BaseModule):
  def post_init(self):
    version_event = Event("__.version__")
    version_event.define(msg_definition="^\.version")
    version_event.subscribe(self)

    # register ourself to our new custom event
    self.bot.register_event(version_event, self)
    
  def handle(self, event):
    self._version(event.channel)

  def _version(self, channel):
    self.say(channel,"I'm running pybot version " + version.__version__)

