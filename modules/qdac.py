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


class Qdac(BaseModule):
    class Qdaction():
        def __init__(self, handle, trigger, action, output):
            self.trigger = trigger
            self.action = action
            self.output = output

    def generate_module(self, qd, event):
        if qd.action == "say":
            self.action = self.say
        self.trigger = qd.trigger
        self.output = qd.output
        new_module = type(
            qd.trigger, (BaseModule,), {
                "handle": self.action, "trigger": self.trigger, "action": self.say, "output": self.output})
        return new_module

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
            self.say(event.channel, self.help)
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

        if self.bot.has_event(new_event):
            self.say(event.channel, "command " + trigger + " already defined.")
            return

        simple_rep = self.Qdaction(qdac_handle, trigger, action, output)
        if "qdac" not in self.bot.persistence:
            qdac_namespace = set()
        else:
            qdac_namespace = self.bot.persistence["qdac"]

        qdac_namespace.add(simple_rep)
        # frozenset or kerblooie
        # https://stackoverflow.com/a/13264725
        self.bot.persist(qdac_namespace)

        new_event.subscribe(new_module)
        self.bot.register_event(new_event, new_module)
        self.say(
            event.channel,
            "Command '" +
            name +
            "' added with trigger " +
            trigger +
            ".")
