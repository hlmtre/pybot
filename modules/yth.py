try:
    from modules.basemodule import BaseModule
except (ImportError, SystemError):
    from .basemodule import BaseModule

from event import Event
import difflib


class YTH(BaseModule):
    def post_init(self):
        command = Event("__.yth__")
        command.define(msg_definition="^\\.yth")
        command.subscribe(self)

        self.bot.register_event(command, self)
        self.help = ".yth, .yth <search terms>"
        self.comparer = difflib.SequenceMatcher()

    def handle(self, event):
        if len(event.msg.split()) == 1:
            count = 0
            msg = list()
            while count < 5 and count < len(self.bot.mem_store['youtube']):
                for entry, url in reversed(
                        list(self.bot.mem_store['youtube'].items())):
                    msg.append(entry + " - " + url)
                    count += 1
            self.say(event.user, ", ".join(msg))
        elif len(event.msg.split()) > 1:  # we're searching for specific terms
            # terms from 1 (ignore .yth) to the end
            terms = event.msg.split()[1:-1]
            msg = list()
            for k, v in list(self.bot.mem_store['youtube'].items()):
                self.comparer.set_seq1(k.lower())
                self.comparer.set_seq2(" ".join(terms))
                if self.comparer.ratio() >= .75:
                    msg.append(k + " - " + v)

            self.say(event.user, ", ".join(msg))
