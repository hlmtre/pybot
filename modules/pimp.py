##Shows the URL to the glorious pybot repo##

import sys
from event import Event

try:
    if sys.version_info > (3, 0, 0):
        from .basemodule import BaseModule
    else:
        from basemodule import BaseModule
except (ImportError, SystemError):
    from modules.basemodule import BaseModule


class Pimp(BaseModule):

    def post_init(self):
        pimp = Event("__.pimp__")
        pimp.define(msg_definition="^\\.pimp$")
        pimp.subscribe(self)
        self.cmd = ".pimp"
        self.help = ".pimp (bot repo URL)"
        self.url = "https://github.com/hlmtre/pybot"

        self.bot.register_event(pimp, self)  # Register your event

    def handle(self, event):
        # Just prints that to the intended channel
        self.say(event.channel, self.url)
