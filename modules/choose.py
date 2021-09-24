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


class Choose(BaseModule):
    def post_init(self):
        choose = Event("__.choose__")
        choose.define(msg_definition="^\\.choose")
        choose.subscribe(self)
        self.bot.register_event(choose, self)
        self.cmd = ".choose"
        self.help = ".choose <option1>|<option2[|<option_n>]"

        for event in self.events:
            if event._type in self.interests:
                event.subscribe(self)

    def handle(self, event):
        try:
            flavortext = ["Always go with ",
                          "I don't always choose, but when I do, I choose ",
                          "Wisdom says you should pick ",
                          "The wise one selects ",
                          "The spinner selects ",
                          "My gut says to go with ",
                          "Easy. I choose ",
                          "I choose "]
            choices = event.msg.split(None, 1)[1].split("|")
            if len(choices) == 1:
                self.say(
                    event.channel,
                    "If you only have one option, the choice is easy. Go with " +
                    choices[0].strip())
                return
            self.say(
                event.channel,
                random.choice(flavortext) +
                random.choice(choices).strip())
        except IndexError:
            self.say(event.channel, "gib choices")
            return
        except Exception as e:
            self.say(event.channel, "I couldn't decide")
            self.bot.debug_print("Error making decision in choice module")
            self.bot.debug_print(str(e))
