import json
import sys
if sys.version_info > (3, 0, 0):
  import urllib.request, urllib.error, urllib.parse
  try:
    from .basemodule import BaseModule
  except (ImportError, SystemError):
    from modules.basemodule import BaseModule
else:
  import urllib2 as urllib
  try:
    from basemodule import BaseModule
  except (ImportError, SystemError):
    from modules.basemodule import BaseModule

from event import Event

class Dad(BaseModule):
  def post_init(self):
    d_event = Event("__.dad__")

    d_event.define(msg_definition="^\.dad")
    d_event.subscribe(self)

    self.bot.register_event(d_event, self)
    self.help = ".dad (prints dad joke)"
  def handle(self, event):
    try:
      url = "https://icanhazdadjoke.com/"
      req = urllib.request.Request(url, headers={'Accept' : "application/json", 'User-Agent' : "Magic Browser"})
      resp = urllib.request.urlopen(req)
      j = json.loads(resp.read())
      self.say(event.channel, j['joke'])
    except:
      pass
