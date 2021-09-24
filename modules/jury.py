#Jury module created by Bonekin#

import random
import sys
from event import Event

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


class Jury(BaseModule):
    def post_init(self):
        jury = Event("__.jury__")
        jury.define(msg_definition="^\\.jury")
        jury.subscribe(self)
        self.help = ".jury (Prints yeas and nays)"

        # register ourself to our new jury event
        self.bot.register_event(jury, self)

    def handle(self, event):
        if event.msg.startswith(".jury"):
            votes = 0
            for i in range(12):
                votes = votes + int(random.choice("01"))
            self.say(event.channel, "Twelve jurors, " + str(votes) +
                     " yeas and " + str((12 - votes)) + " nays.")
