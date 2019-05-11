## version 0.1 created by hlmtre ##
## version 0.2 updated by mech ##

from event import Event
try:
  import requests
except ImportError:
  print "Warning: isup module requires requests"
  requests = object
import json
try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule

class Isup(BaseModule):
  def post_init(self):
    isup = Event("__.isup__")
    isup.define(msg_definition="^\.isup")
    isup.subscribe(self)
    self.help = ".isup <Valid website using *.com, *.net, etc.>"

    # register ourself to our new isup event
    self.bot.register_event(isup, self)

    self.url = "https://api.downfor.cloud/httpcheck/" # URL which outputs JSON data

    """
    Example to show json data parameters that can be pulled from with current URL get request:

    statusCode	200
    statusText	"OK"
    isDown	false
    returnedUrl	"https://www.reddit.com/"
    requestedDomain	"reddit.com"
    lastChecked	1557603603861
    """
  def handle(self, event):
    if len(event.msg.split()) == 2: # Looks for the command and hopefully a valid website (*.com,*.net, etc.)
      try:
        r = requests.get(self.url + event.msg.split()[1]) # Takes our static URL and appends your site to the end to make our get request
        j = json.loads(r.text) # Converts our JSON to python object
        if str(j["isDown"]) == "True": # Converts our parameter to a string to compare against our "isDown" parameter
          self.say(event.channel, "Site looks down; it's not just you.") # Once state is determined it will be spit out into the channel
        elif str(j["isDown"]) == "False":
          self.say(event.channel, "Site looks ok to me; it's just you.")

      except requests.ConnectionError:
        self.say("Connection error.")
