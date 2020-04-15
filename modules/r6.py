## r6 created by mech ##
##  A simple progam to pull stats using r6tab ##

import sys
import json
from event import Event
try:
  import requests
except (ImportError, SystemError):
  print("Warning: r6 module requires requests")
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
  """ Takes specified stats from r6tab and prints them to irc channel """
  def post_init(self):
    r6 = Event("__.r6__")
    r6.define(msg_definition=r"^\.r6")
    r6.subscribe(self)
    self.help = ".r6 <kd,level,rank> <gamer-tag>"
    # register ourself to our new r6 event
    self.bot.register_event(r6, self)

    self.url = "https://r6.apitab.com/search/uplay/" # URL which outputs JSON data

    """
    Example to show json data parameters that can be pulled from with current URL get request:

    level	107
    ranked	
    kd	0.7
    mmr	1881
    rank	6
    champ	0
    NA_mmr	1881
    NA_rank	0
    NA_champ	0
    EU_mmr	0
    EU_rank	0
    EU_champ	0
    AS_mmr	0
    AS_rank	0
    AS_champ	0
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
        if j['foundmatch'] == False:
          self.say(event.channel, "Player not found.")
          return
        for value in j['players']: # Each player has a unique player ID that needs to be grabbed to drill down to the rest of the data
          p_id = value
        level = str(j['players'][p_id]['stats']['level']) # Different parameters to choose from
        kd = str(j['players'][p_id]['ranked']['kd'])
        rank = str(j['players'][p_id]['ranked']['mmr'])
        if event.msg.split()[1] == "rank":
          self.say(event.channel, rank)
        elif event.msg.split()[1] == "kd":
          self.say(event.channel, kd)
        elif event.msg.split()[1] == "level":
          self.say(event.channel, level)

      except requests.ConnectionError:
        self.say(event.channel, "Connection error.")
      except KeyError:
        self.say(event.channel, "Player not found.")
