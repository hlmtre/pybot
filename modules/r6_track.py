## r6_track created by mech ##
##  A simple progam to pull stats using r6tab ##

import sys
import json
from event import Event
try:
  import requests
except (ImportError, SystemError):
  print("Warning: r6_track module requires requests")
  requests = object
if sys.version_info > (3, 0, 0):
  try:
    from .basemodule import BaseModule
  except (ImportError, SystemError):
    from modules.basemodule import BaseModule
else:
  try:
    from basemodule import BaseModule
  except (ImportError, SystemError):
    from modules.basemodule import BaseModule

class R6(BaseModule):
  """ Takes specified stats from r6 tracker and prints them to irc channel """
  def post_init(self):
    r6 = Event("__.r6__")
    r6.define(msg_definition=r"^\.r6")
    r6.subscribe(self)
    self.help = ".r6 <stat> <gamer tag>"

    # register ourself to our new r6_track event
    self.bot.register_event(r6, self)

    self.url = "https://r6tab.com/api/search.php?platform=uplay&search=" # URL which outputs JSON data

    """
    Example to show json data parameters that can be pulled from with current URL get request:

    p_id	"b3a7f575-6689-40ff-9a88-a752299736b2"
    p_name	"mechmaster7"
    p_level	100
    p_platform	"uplay"
    p_user	"b3a7f575-6689-40ff-9a88-a752299736b2"
    p_currentmmr	1838
    p_currentrank	6
    verified	0
    kd	67
    totalresults	1
    """
  def handle(self, event):
    if len(event.msg.split()) == 3: # Looks for the command and hopefully a valid website (*.com,*.net, etc.)
      try:
        """Needed to set user agent so request would not be blocked, without this a 503 status code is returned"""
        headers = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                }
        r = requests.get(self.url + event.msg.split()[2], headers=headers)# Takes our static URL and appends your site to the end to make our get request
        j = json.loads(r.text) # Converts our JSON to python object
        mmr = str(j["results"][0]["p_currentmmr"])
        kd = str(j["results"][0]["kd"])
        if event.msg.split()[1] == "mmr":
          self.say(event.channel, mmr)
        """The block below is needed because the json data for kd is just an integer and needs to be a decimal number for kd"""
        elif event.msg.split()[1] == "kd":
          if len(kd) == 3:
            split = list(kd)
            split.insert(1, ".")
            self.say(event.channel, str("".join(split)))
          else:
            self.say(event.channel,"." +  kd)

      except requests.ConnectionError:
        self.say(event.channel, "Connection error.")
      except KeyError:
        self.say(event.channel, "Player not found.")
