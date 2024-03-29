# vim: tabstop=2 shiftwidth=2
import re


class Event:
    """
    Allows event type definition. The definition accepts a regex.
    Every event can be triggered by specific lines, messages, message_id or users.
    Eventually (see time_event branch for proof-of-concept implementation) time-sensitive events will be triggerable as well.

    Each line received by the bot is passed to each module in the modules_list. If the module determines the line matches what the event cares about,
    the event calls each of its subscribers itself, which contains all the information the module needs to respond appropriately.

    To use:
      e = Event("__my_type__")
      e.define("some_regex")
      bot.register_event(e, calling_module)
    """

    def __init__(self, _type):
        """
        Define your own type here. Make sure if you're making a broad event (all messages, for example) you use a sane type, as other modules that care about this kind of event can subscribe to it.

        Args:
        _type: string. like "__youtube__" or "__weather__". Underscores are a convention.
        """
        self._type = _type
        self.subscribers = []  # this is a list of subscribers to notify
        self.user = ""
        self.definition = ""
        self.msg_definition = ""
        self.user_definition = ""
        self.channel = ""
        self.line = ""
        self.msg = ""
        self.verb = ""
        self.mode = ""
        self.is_pm = False
        self.message_id = -1
        self.case_insensitive = False

    def subscribe(self, e):
        """
        Append passed-in event to our list of subscribing modules.

        Args:
        e: event.
        """
        self.subscribers.append(e)

    def define(self, definition=None, msg_definition=None, user_definition=None,
               message_id=None, mode=None, case_insensitive=False):
        """
        Define ourself by general line (definition), msg_definition (what someone says in a channel or PM), user_definition (the user who said the thing), or message_id (like 376 for MOTD or 422 for no MOTD)
        Currently, an event is defined by only one type of definition. If one were to remove the returns after each self. set, an event could be defined and triggered by any of several definitions.

        Args:
        definition: string. regex allowed.
        msg_definition: string. regex allowed. this is what someone would say in a channel. like "hello, pybot".
        user_definition: string. the user that said the thing. like 'hlmtre' or 'BoneKin'.
        message_id: the numerical ID of low-level IRC protocol stuff. 376, for example, tells clients 'hey, this is the MOTD.'
        """
        if definition is not None:
            self.definition = definition
        if msg_definition is not None:
            self.msg_definition = msg_definition
        if user_definition is not None:
            self.user_definition = user_definition
        if message_id is not None:
            self.message_id = message_id
        if mode is not None:
            self.mode = mode
        self.case_insensitive = case_insensitive

        return

    def matches(self, line):
        """
        Fills out the event object per line, and returns True or False if the line matches one of our definitions.
        Args:
        line: string. The entire incoming line.

        Return:
        boolean; True or False.
        """
        # perhaps TODO
        # first try very simply
        if len(self.definition) and self.definition in line:
            return True
        # grab message id. not always present
        try:
            temp = line.split(":")[1].split(" ")[1]
        except IndexError:
            pass

        if len(self.mode):
            try:
                split_line = line.split()
                temp_verb = split_line[1]  # first nick, then verb
                if self.mode == temp_verb.strip():
                    return True
            except IndexError:
                pass

        try:
            message_id = int(temp)
        except (ValueError, UnboundLocalError):
            message_id = 0

        try:
            msg = line.split(":", 2)[2]
        except IndexError:
            return

        if len(self.msg_definition):
            if self.case_insensitive:
                return re.search(self.msg_definition, msg, re.IGNORECASE)
            else:
                return re.search(self.msg_definition, msg)

        if len(self.definition):
            if re.search(self.definition, line):
                return True

        if len(self.user_definition):
            if line and "PRIVMSG" in line:
                line_array = line.split()
                user_and_mask = line_array[0][1:]
                user = user_and_mask.split("!")[0]
                if self.user_definition == user:
                    return True

        if isinstance(self.message_id, int):
            if self.message_id == message_id:
                return True

        return False

    def notifySubscribers(self, line):
        """
        Fills out the object with all necessary information, then notifies subscribers with itself (an event with all the line information parsed out) as an argument.
        Args:
        line: string

        """
        self.line = line
        if line == "null":
            for s in self.subscribers:
                s.handle(self)
            return
        self.user = line.split(":")[1].rsplit(
            "!")[0]  # nick is first thing on line
        if "JOIN" in line or "QUIT" in line:
            self.user = line.split("!")[0].replace(":", "")
        try:
            temp = line.split(":")[1].split(" ")[1]
        except IndexError:
            pass

        try:
            self.msg = line.split(":", 2)[2]
        except IndexError:
            self.msg = ""

        l = line.split()
        self.channel = ""
        self.verb = ""
        ind = 0
        for e in l:
            ind += 1
            if e == "PRIVMSG":
                pass
            if e.startswith("#"):
                self.channel = e
                break
        for v in l:
            if v.strip() in ["JOIN", "PART", "QUIT", "NICK", "KICK",
                             "PRIVMSG", "TOPIC", "NOTICE", "PING", "PONG", "MODE"]:
                self.verb = v
                break
        # channel is unset if it does not begin with #
        if self.verb == "PRIVMSG" and not len(self.channel):
            self.is_pm = True
        for s in self.subscribers:
            try:
                s.handle(self)
            except AttributeError:
                pass
