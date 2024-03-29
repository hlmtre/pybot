# -*- coding: utf-8 -*-

##Converts celcius to farenheit##

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


class Ctof(BaseModule):

    def post_init(self):
        ctof = Event("__.ctof__")
        ctof.define(msg_definition="^\\.ctof")
        ctof.subscribe(self)
        self.cmd = ".ctof"
        self.help = ".ctof [celsius]"

        self.bot.register_event(ctof, self)

    def handle(self, event):
        try:

            if event.msg.startswith(".ctof"):
                # Splits number from command, "['.ctof', '<some number>']"
                split_msg = event.msg.split()
                c_temp = split_msg[1]
                c = float(c_temp)
                # Does the math from celcius to freedom units
                f = (c * 1.8) + 32
                # Spits the conversion into the proper channel
                self.say(event.channel, str(round(f, 1)) + "° F")

        except ValueError:
            self.say(event.channel, "Enter a number you rube!")
        except IndexError:
            self.say(event.channel, "Try '.ctof [celcius]'")
