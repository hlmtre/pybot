#Created by hlmtre#

"""
Works only in hlmtre's specifically  configured environment
and when his house has not burned down
"""

import sys
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

from event import Event


class Vyos(BaseModule):
    def post_init(self):
        vevent = Event("__.vyos__")
        vevent.define(msg_definition="^\\.vyos")
        vevent.subscribe(self)
        self.help = ".vyos <name of box>"
        self.box_to_ip = dict(
            [('mech', '10.0.0.76'), ('bonekin', '192.168.17.40'), ('thraust', '192.168.0.126')])

        self.bot.register_event(vevent, self)

    def handle(self, event):
        self.event = event
        if event.msg.startswith(".vyos") and len(event.msg.split()) > 1:
            nick = event.msg.split()[-1]
            if not self.ping(nick):
                self.say(
                    event.channel,
                    "HEY " +
                    nick.upper() +
                    " UR VYOS BAWKCXZXCZX IS DOWN")
            else:
                self.say(
                    event.channel,
                    "HEY " +
                    nick.upper() +
                    " U KEPT SOMETHING ALIVE 4 ONCE")

    def ping(self, nick):
        import subprocess
        try:
            resp = subprocess.call(
                ["ping", "-c 1", self.box_to_ip[nick.lower()]])
        except KeyError:
            self.say(self.event.channel, "BAD NAME IDIOT")
            return False
        if resp == 0:
            return True
        else:
            return False
