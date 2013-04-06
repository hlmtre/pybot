import sys
import urllib2
import json
class LastFM:
  def __init__(self, events=None, printer_handle=None, bot=None):
    self.bot_handle = bot
    self.events = events
    self.printer = printer_handle
    self.interests = ['__.lastfm__']
    for event in events:
      if event._type in self.interests:
        print "DEBUG: registering to ",
        print event
        event.subscribe(self)

  def handle(self, event):
    msg = event.line.rsplit(":")[-1]
    if msg.startswith(".lastfm add"):
      lastfm_username = msg.split()[-1]
      self.bot_handle.db.e("REPLACE INTO lastfm (lastfm_username, nick) VALUES ('" + lastfm_username + "', '" + event.user + "')")
    else:
      try:
        username = self.bot_handle.db.e("SELECT lastfm_username FROM lastfm WHERE nick = '" + event.user + "'")[0][0]
        api_key = "80688df02fc5af99f1ed97b5f667f0c4"
        url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user="+username+"&api_key="+api_key+"&format=json"
        response = urllib2.urlopen(url)
        text = response.read()
        j = json.loads(text)

        #f = open("/home/hlmtre/bin/json_out","w+")

        try:
          if "@attr" in j["recenttracks"]["track"][0]:
            if j["recenttracks"]["track"][0]["@attr"]["nowplaying"] == "true":
              output = j["recenttracks"]["track"][0]['artist']['#text'] + " - " + j["recenttracks"]["track"][0]['name'] 
              self.printer("PRIVMSG " + event.channel + " :" + event.user + " is now playing: " + output + '\n')
        except Exception, e:
          print j

      except IndexError:
        self.printer("PRIVMSG " + event.channel + " : no lastfm username for " + event.user + '\n')
