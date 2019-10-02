#Simple module to spit out the time in a city specified by user, poorly thrown together by mech
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
    self.help = ".tzone <Insert location name/zip/airport(SFO,PDX,etc.)>"
    self.bot.register_event(tzone, self)
    self.url = "https://dev.virtualearth.net/REST/v1/TimeZone/query="
    self.key = "?key=AuEaLSdFYvXwY4u1FnyP-f9l5u5Ul9AUA_U1F-eJ-8O_Fo9Cngl95z6UL0Lr5Nmx"
#TODO put in a minor work around for places like Chico california not working with just '.tzone Chico'
#TODO split out verifying the location request is properly formatted into its own function.
  def request_api(self, location):
    """Takes the location provided and determines whether its a valid request
    and will return either the time of the location or a message instructing you
    how to the make the proper call"""
    url_query = None
    try:
      headers = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
      }
      url_query = self.url + location + self.key
      r = requests.get(url_query, headers=headers)
      j = json.loads(r.text)
      local_time_date = j["resourceSets"][0]["resources"][0]["timeZoneAtLocation"][0]["timeZone"][0]["convertedTime"]["localTime"].split("T")
      place = j["resourceSets"][0]["resources"][0]["timeZoneAtLocation"][0]["placeName"]
      """Checks to see if request is specific enough for one timezone"""
      multiple_locations = j["resourceSets"][0]["resources"][0]["timeZoneAtLocation"][0]["timeZone"]
      if len(multiple_locations) > 1:
        return "Multiple timezones returned, try being more specific"
      else:
        return str(place + ": " + local_time_date[1])
    except IndexError:
      return "Not a valid request, try again."
    except ValueError:
      return "Not a valid request, try again."
    except KeyError:
      return "Not a valid request, try again."

  def handle(self, event):
    try:
      if event.msg.startswith(".tzone"):
        split_tz = event.msg.split()
        if len(split_tz) > 2:
          tz = "+".join(split_tz[1:])
        else:
          tz = split_tz[1].lower()
      self.say(event.channel, self.request_api(tz))
    except TypeError:
      pass # Error gets caught here and in ValueError in request_api function
