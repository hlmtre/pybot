#BOFH quote module created by hlmtre#

from event import Event
import sys
import random

try:
    import requests
except (ImportError, SystemError):
    print("bofh requires requests pip module")
    requests = None

try:
    if sys.version_info > (3, 0, 0):
        from .basemodule import BaseModule
    else:
        from basemodule import BaseModule
except (ImportError, SystemError):
    from modules.basemodule import BaseModule


class Bofh(BaseModule):
    def post_init(self):
        b_event = Event("__.bofh__")

        b_event.define(msg_definition="^\\.bofh$")
        b_event.subscribe(self)

        self.bot.register_event(b_event, self)
        self.help = ".bofh (prints random quote)"

    def handle(self, event):
        try:
            r = requests.get('http://pages.cs.wisc.edu/~ballard/bofh/excuses')
            r_text = r.text
            r_list = r_text.split('\n')
            self.say(event.channel, "BOFH: " +
                     r_list[random.randrange(0, len(r_list))])
        except BaseException:
            pass
