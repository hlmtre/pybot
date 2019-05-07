import urllib2
import json
from event import Event
try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule
class Dad(BaseModule):
  def post_init(self):
    d_event = Event("__.dad__")

    d_event.define(msg_definition="^\.dad")
    d_event.subscribe(self)

    self.bot.register_event(d_event, self)
    self.help = ".dad 'prints dad joke'"
  def handle(self, event):
    try:
      url = "https://icanhazdadjoke.com/"
      req = urllib2.Request(url, headers={'Accept' : "application/json", 'User-Agent' : "Magic Browser"})
      resp = urllib2.urlopen(req)
      j = json.loads(resp.read())
      self.say(event.channel, j['joke'])
    except:
      pass
