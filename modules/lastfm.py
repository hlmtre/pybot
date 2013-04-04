import sys
import urllib2
import json
class LastFM:
  def __init__(self, events, printer_handle):
    self.events = events
    self.printer = printer_handle
    self.interests = ['__.lastfm__']
    for event in events:
      if event._type in self.interests:
        print "DEBUG: registering to ",
        print event
        event.subscribe(self)

  def handle(self, event):
    username = event.line.split()[-1]
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

