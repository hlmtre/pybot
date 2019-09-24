##Simple module to spit out the time in a city specified by user, poorly thrown together by mech##
 
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
    try:
      if event.msg.startswith(".tzone"): #Splits the option from the ".tzone" command to be used to find the proper timezone
        headers = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                }
        split_tz = event.msg.split()
#        print(split_tz)
        if len(split_tz) > 2:
          tz = "+".join(split_tz[1:])
        else:
          tz = split_tz[1].lower()
        link = "https://dev.virtualearth.net/REST/v1/TimeZone/query=%s?key=AuEaLSdFYvXwY4u1FnyP-f9l5u5Ul9AUA_U1F-eJ-8O_Fo9Cngl95z6UL0Lr5Nmx" % tz
#        print(link)
        r = requests.get(link, headers=headers)
        j = json.loads(r.text)
#        test_local_time = j["resourceSets"][0]["resources"][0]["__type"]["timeZoneAtLocation"]
#        print(len(test_local_time))
        local_time_date = j["resourceSets"][0]["resources"][0]["timeZoneAtLocation"][0]["timeZone"][0]["convertedTime"]["localTime"]
        local_time = local_time_date.split("T")
        self.say(event.channel, local_time[1])
    except IndexError: #Handles the 2 errors I have found based on user error
      self.say(event.channel, "Idk what you did, but it was wrong.")
    except ValueError:
      self.say(event.channel, "If this error message came up then this is still valid and you should make a better message you muppet!")
    except KeyError:
      self.say(event.channel, "Not a valid location or multiple results, try being more specific.")
