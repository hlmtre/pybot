# Simple module to spit out the time in a city specified by user, poorly
# thrown together by mech
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
        tzone.define(msg_definition="^\\.tzone")
        tzone.subscribe(self)
        self.cmd = ".tzone"
        self.help = ".tzone <Insert location name/zip/airport(SFO,PDX,etc.)>"
        try:
            from bing_credentials import BingCredentials
        except (ImportError, SystemError):
            print(
                "Warning: tzone module requires credentials in modules/bing_credentials.py")

            class PhonyBc:
                api_key = "None"

        self.bot.register_event(tzone, self)
        self.url = "https://api.geotimezone.com/public/timezone"
        # self.url = "https://dev.virtualearth.net/REST/v1/TimeZone/query="
        # self.key = "?key=AuEaLSdFYvXwY4u1FnyP-f9l5u5Ul9AUA_U1F-eJ-8O_Fo9Cngl95z6UL0Lr5Nmx"
# TODO split out verifying the location request is properly formatted into
# its own function.

    """Take the location provided and determine whether it's a valid request
    Then return either the time of the location or a message instructing you
    how to the make the proper call"""

    def request_api(self, location):
        from modules.bing import Bing
        b = Bing()
        lat, long = b.get_lat_long_from_bing(location)
        url_query = None
        try:
            headers = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            }
            url_query = self.url + "?latitude=" + str(lat) + "&longitude=" + str(long)
            r = requests.get(url_query)
            j = json.loads(r.text)
            print(json.dumps(j, indent=2))
            local_time = j["current_local_datetime"].split("T")[-1]
            return str(location + ", (assumed to be timezone " + j["iana_timezone"] + ", " + j["offset"] + "): " + local_time)
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
        except TypeError as e:
            self.say(event.channel, "error!")
            print(e)
