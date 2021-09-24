##Lists modules and usage##

from event import Event
import sys
try:
    if sys.version_info > (3, 0, 0):
        from .basemodule import BaseModule
    else:
        from basemodule import BaseModule
except (ImportError, SystemError):
    from modules.basemodule import BaseModule


class Help(BaseModule):
    def post_init(self):
        help = Event("__.help__")
        help.define(msg_definition="^\\.help")
        help.subscribe(self)
        self.cmd = ".help"

        # register ourself to our new custom event
        self.bot.register_event(help, self)

    def handle(self, event):
        l = event.msg.split()
        if l[0] == ".help" and len(l) > 1:
            self.individual_help(l[1], event)
            return
        try:
            line_list = self.get_help_lines()
            """
      This janky block controls how many modules to print per line
      To change the amount of modules print per line change the first 'q' to whatever number and match the incremented 'q and f' to the same number
      """
            # TODO make it better, probably pull out into a function
            self.say(event.user, "Help: \n")
            q = 3  # sets the starting end index
            # sets the index to start from (The beginning of the list usually)
            f = 0
            for h in range(len(line_list)):
                # Prints the line in a private message for each slice
                self.say(event.user, ", ".join(line_list[f:q]))
                q += 3  # increments the end index
                f += 3  # increments the start index
                if q >= len(line_list):
                    break
        except BaseException:
            pass

    def get_help_lines(self):
        modules_set = set()
        for m in self.bot.events_list:
            for s in m.subscribers:
                modules_set.add(s)

        line_list = list()

        for sm in modules_set:
            if hasattr(sm, "help") and sm.help is not None:
                line_list.append(sm.help)
        return line_list

    def individual_help(self, cmd, event):
        line_list = self.get_help_lines()
        matching_lines = list()
        for line in line_list:
            if cmd in line:
                matching_lines.append(line)
        if len(matching_lines) > 0:
            self.bot.say(event.user, "Help for matching commands: \n")
            for line in matching_lines:
                self.bot.say(event.user, line + "\n")
        else:
            self.bot.say(event.user, "No matching commands :(")
        return
