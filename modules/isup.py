## version 0.1 created by hlmtre ##
## version 0.2 updated by mech ##

import sys
import json
from event import Event
try:
    import requests
except (ImportError, SystemError):
    print("Warning: isup module requires requests")
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


class Isup(BaseModule):
    """ takes a url and determines if the site hosted there is up """

    def post_init(self):
        isup = Event("__.isup__")
        isup.define(msg_definition=r"^\.isup")
        isup.subscribe(self)
        self.help = ".isup <Valid website using *.com, *.net, etc.>"

        # register ourself to our new isup event
        self.bot.register_event(isup, self)

        self.url = "https://api.downfor.cloud/httpcheck/"  # URL which outputs JSON data

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
        if len(event.msg.split(
        )) == 2:  # Looks for the command and hopefully a valid website (*.com,*.net, etc.)
            try:
                """Needed to set user agent so request would not be blocked, without this a 503 status code is returned"""
                headers = {
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
                }
                # Takes our static URL and appends your site to the end to make
                # our get request
                r = requests.get(
                    self.url + event.msg.split()[1],
                    headers=headers)
                j = json.loads(r.text)  # Converts our JSON to python object
                # Converts our parameter to a string to compare against our
                # "isDown" parameter
                if str(j["isDown"]) == "True":
                    # Once state is determined it will be spit out into the
                    # channel
                    self.say(event.channel,
                             "Site looks down; it's not just you.")
                elif str(j["isDown"]) == "False" and j["statusCode"] == 200:
                    self.say(event.channel,
                             "Site looks ok to me; it's just you.")

            except requests.ConnectionError:
                self.say("Connection error.")
