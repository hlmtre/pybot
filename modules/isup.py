from event import Event
try:
  import requests
except ImportError:
  print "Warning: isup module requires requests."
  requests = object
from xml.dom.minidom import parseString
try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule
class Isup(BaseModule):
  def post_init(self):
    isup = Event("__.isup__")
    isup.define(msg_definition="^\.isup")
    isup.subscribe(self)
    self.help = ".isup <website of interest>"

    # register ourself to our new isup event
    self.bot.register_event(isup, self)

    self.url = "http://isup.me/"
    
  def handle(self, event):
    print("MADE IT HERE") 
    if len(event.msg.split()) == 2:
      try:
        r = requests.get(self.url + event.msg.split()[1])
        print(r)
      except requests.ConnectionError:
        #self.say(event.channel, "Connection error.")
        print("NO CONNECTION")
      # we get back plain HTML. hopefully the phrases don't change.
      print(r)
      up = "It's just you."
      down = "looks down from here"
      not_a_site = "doesn't look like a site"
      if r.text.find(up) != -1:
        self.say(event.channel, event.msg.split()[1] + " looks up.")
      elif r.text.find(not_a_site) != -1:
        self.say(event.channel, event.msg.split()[1] + " is not a site.")
      elif r.text.find(down) != -1:
        self.say(event.channel, event.msg.split()[1] + " looks down.")
        
