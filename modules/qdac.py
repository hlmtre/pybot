import random
import sys
from pprint import pprint
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


class Qdac(BaseModule):
    def post_init(self):
        qdac = Event("__.qdac__")
        qdac.define(msg_definition="^\\.qdac")
        qdac.subscribe(self)
        self.help = ".qdac <trigger> <action to take: [say]> <thing to say>"

        self.bot.register_event(qdac, self)

    def handle(self, event):
        def qdac_handle(event):
            action = event.subscribers[0].action
            trigger = event.subscribers[0].trigger
            output = event.subscribers[0].output
            action(event.channel, output)

        words = event.msg.split(" ", maxsplit=3)
        if not len(words) == 4:
            self.say(event.channel, "qdac: invalid command format")
            return

        trigger, action, output = words[1], words[2], words[3]
        # TODO ADD MORE ABILITIES HERE
        # we have to check it here to verify our actions are safe
        if action == "say":
            fn = self.say
        new_event = Event("__" + trigger + "__")
        new_event.define(msg_definition="^\\" + trigger)
        name = trigger.strip(".").upper()
        new_module = type(
            name, (BaseModule,), {
                "handle": qdac_handle, "trigger": trigger, "action": fn, "output": output})
        new_event.subscribe(new_module)
        self.bot.register_event(new_event, new_module)
        self.say(
            event.channel,
            "Command '" +
            name +
            "' added with trigger " +
            trigger +
            ".")
