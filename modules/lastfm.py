##Lastfm module created by hlmtre##

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

class LastFM(BaseModule):

  def post_init(self):
    lastfm = Event("__.lastfm__")
    lastfm.define(msg_definition=r"^\.lastfm")
    lastfm.subscribe(self)
    self.help = ".lastfm add <lastfm username> then .last"

    # register ourself to our new custom event
    self.bot.register_event(lastfm, self)

  def handle(self, event):
    msg = event.line.rsplit(":")[-1]
    # replace username in db if their nick already exists; otherwise insert new row
    if msg.startswith(".lastfm add"):
      lastfm_username = msg.split()[-1]
      try:
        self.bot.db.e("REPLACE INTO lastfm (lastfm_username, nick) VALUES ('" + lastfm_username + "', '" + event.user + "')")
      except Exception as e:
        print(e)
    elif msg.startswith(".lastfm"):
      try:
      # go get it
        username = self.bot.db.e("SELECT lastfm_username FROM lastfm WHERE nick = '" + event.user + "'")[0][0]
        api_key = "80688df02fc5af99f1ed97b5f667f0c4"
        url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user="+username+"&api_key="+api_key+"&format=json"
        if sys.version_info > (3, 0, 0): # py3 has requests built in, and incorporated urllib functions
          response = urllib.request.urlopen(url)
        else:
          response = urllib.urlopen(url)
        text = response.read()
        j = json.loads(text.decode())
        if "@attr" in j["recenttracks"]["track"][0]:
          if j["recenttracks"]["track"][0]["@attr"]["nowplaying"] == "true":
            output = j["recenttracks"]["track"][0]['artist']['#text'] + " - " + j["recenttracks"]["track"][0]['name']
            self.say(event.channel, event.user + " is now playing: " + output) # What you are currently listening to
        else:
          output = j["recenttracks"]["track"][0]['artist']['#text'] + " - " + j["recenttracks"]["track"][0]['name']
          self.say(event.channel, event.user + " recently played: " + output) # If not listening anymore, what you were listening to

      except IndexError as e:
        print(e)
        self.say(event.channel, "no lastfm username for " + event.user)
