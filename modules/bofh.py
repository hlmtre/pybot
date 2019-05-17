from event import Event
import sys
try:
  if sys.version_info > (3, 0, 0):
    from .basemodule import BaseModule
    import urllib.request, urllib.error, urllib.parse
  else:
    import urlllib2 as urllib
    from basemodule import BaseModule
except (ImportError, SystemError):
  from modules.basemodule import BaseModule

class Bofh(BaseModule):
  def post_init(self):
    b_event = Event("__.bofh__")

    b_event.define(msg_definition="^\.bofh")
    b_event.subscribe(self)

    self.bot.register_event(b_event, self)
    self.help = ".bofh (prints random quote)"
  def handle(self, event):
    try:
      url = "http://zero9f9.com/api/bofh"
      response = urllib.request.urlopen(url)
      text = response.read()
      bofhquote = text.splitlines()[2]
      self.say(event.channel, "BOFH: " + bofhquote)
    except:
      pass
