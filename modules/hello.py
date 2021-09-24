##Created by hlmtre, just pybot giving a friendly hello##

import sys
from event import Event
from random import choice

try:
    if sys.version_info > (3, 0, 0):
        from .basemodule import BaseModule
    else:
        from basemodule import BaseModule
except (ImportError, SystemError):
    from modules.basemodule import BaseModule


class Hello(BaseModule):

    def post_init(self):
        hello = Event("__hello__")
        hello.subscribe(self)
        self.help = None
        self.bot.register_event(hello, self)  # Register to your event

        # Grabs the nick of the person greeting pybot
        nick = self.bot.conf.getNick(self.bot.network)
        # How pybot determines whether he is being greeted
        hello.define(
            msg_definition="^([H|h]ello|[H|h]i|[H|h]owdy|[H|h]ey) " +
            nick)
        # List of different ways he will be able to respond
        self.retorts = ['hello', 'sup', 'hi', 'good to see you', 'loldicks']

    def handle(self, event):
        try:
            # If the parameters above in "hello.define" are met he will spit
            # out the greeting in the channel
            self.say(event.channel, choice(self.retorts) + " " + event.user)
        except Exception as e:
            print(e)
