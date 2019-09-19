##Simple module to spit out the time in a certain area/timezone, poorly thrown together by mech##

import sys
import json
from event import Event
try:
  import requests
except (ImportError, SystemError):
  print("Warning: tzone module requires requests")
  requests = object

try:
  if sys.version_info > (3, 0, 0):
    from .basemodule import BaseModule
  else:
    from basemodule import BaseModule
except (ImportError, SystemError):
  from modules.basemodule import BaseModule

class Tzone(BaseModule):
  def post_init(self):
    tzone = Event("__.tzone__")
    tzone.define(msg_definition="^\.tzone")
    tzone.subscribe(self)
    self.cmd = ".tzone"
    self.help = ".tzone <Insert location name>"

    self.bot.register_event(tzone, self)

  def handle(self, event):
#    lat_long_url = "https://geocode.xyz/Hauptstr.,+57632+%s?json=1" % location # placeholder for optional user defined location
#    location_url = "http://api.geonames.org/timezoneJSON?lat=%s&lng=%s&username=demo" % (lat,lon) # placeholder for optional user defined location
    try:
      if event.msg.startswith(".tzone"): #Splits the option from the ".tzone" command to be used to find the proper timezone
        headers = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                }
        split_tz = event.msg.split()
        tz = split_tz[1].lower()
        lat_long_url = "https://geocode.xyz/Hauptstr.,+57632+%s?json=1" % tz # placeholder for optional user defined location
        r1 = requests.get(lat_long_url, headers=headers)
        j1 = json.loads(r1.text)
        lat = str(j1["latt"])
        lon = str(j1["longt"])
        location_url = "http://api.geonames.org/timezoneJSON?lat=%s&lng=%s&username=test1" % (lat,lon) #Username registered is muhmail (test1 is placeholder)
        r2 = requests.get(location_url, headers=headers)
        j2 = json.loads(r2.text)
        time = str(j2["time"])
#        print(j1)
#        print(lat_long_url)
#        print(split_tz)
#        print(tz)
        print(lat)
        print(lon)
        print(j2)
        print(location_url)
        print(time)
        self.say(event.channel, time)
    except IndexError: #Handles the 2 errors I have found based on user error
      self.say(event.channel, "Idk what you did, but it was wrong.")
    except ValueError:
      self.say(event.channel, "If this error message came up then this is still valid and you should make a better message you muppet!")
    except KeyError:
      self.say(event.channel, "Not a valid location or multiple results, try being more specific.")
