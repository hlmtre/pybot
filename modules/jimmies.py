#Jimmies module created by Bonekin#
from __future__ import print_function

from event import Event
import random
import sys

try:
    if sys.version_info > (3, 0, 0):
        from .basemodule import BaseModule
    else:
        from basemodule import BaseModule
except (ImportError, SystemError):
    from modules.basemodule import BaseModule


class Jimmies(BaseModule):

    def post_init(self):
        jimmies = Event("__.jimmies__")
        jimmies.define(msg_definition="^\\.jimmies")
        jimmies.subscribe(self)
        self.cmd = ".jimmies"
        self.help = ".jimmies <nick>"

        # Register ourself to our new custom event
        self.bot.register_event(jimmies, self)

    def get_jimmies_status(self):
        """Randomly selects and returns a string with a "jimmies" status."""
        status = [" Rustled [ ] Not Rustled",
                  "Rustled as fuck",
                  "Rustled as fuark",
                  "Rustled 'n' hustled",
                  "Professor James  R. Russel, Department of Primatology",
                  "le monkey face",
                  "No rustling. Only dreams now.",
                  "Y'all rusting in a jimmies thread",
                  "Haha. Oh god. Mah jimmies.",
                  "The jimmies have been compromised.",
                  "A gorillion jimmies.",
                  "Boku no rustled",
                  "Rustle of the Planet of the Jimmies",
                  "You just rustled my jimmy card",
                  "Micky Rourke as The Rustler",
                  ">he thinks his jimmies are unrustled",
                  "WWE Rustlemania",
                  "Teach Me How To Jimmie",
                  "#3 Rustle Wilson",
                  "Rustle-it Ralph",
                  "All those people. All that rustling.",
                  "Rustle Brand",
                  "Everyone's getting rustled!",
                  "Did someone rustle your jimmies? Show me on the doll where they rustled you.",
                  "Oh shit! My jimmies!"
                  ]
        return "[X] " + random.choice(status)

    def handle(self, event):
        _z = event.msg.split(None, 1)
        # Gets the jimmies status from the list above
        jimmies_status = self.get_jimmies_status()
        try:
            # Prints the jimmies status to the proper channel if a user is
            # specified properly
            self.say(
                event.channel,
                "Jimmies status for " +
                _z[1] +
                ": " +
                jimmies_status)
        except IndexError:
            self.say(
                event.channel,
                "You didn\'t specify whose jimmies you wanted to check. " +
                event.user +
                "\'s jimmies status: " +
                jimmies_status)  # Spits into channel if user not specified correctly
        except TypeError:
            print("DEBUG: TypeError: ", end=' ')
            print(event.channel, end=' ')
            print(event.user)
