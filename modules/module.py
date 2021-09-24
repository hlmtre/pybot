from logger import Logger
from event import Event


class Module:
    def __init__(self, events=None, printer_handle=None, bot=None, say=None):
        self.events = events
        self.printer = printer_handle
        self.bot = bot
        self.interests = []
        self.say = say

        self.cmd = None
        self.help = None

        mod = Event("__.module__")
        mod.define(msg_definition="^\\.module ")
        mod.subscribe(self)

        self.bot.register_event(mod, self)

        # for event in events:
        #  if event._type in self.interests:
        #    event.subscribe(self)

    def handle(self, event):
        if not self.bot.brain._isAdmin(
                event.user):  # guard the entire function under this
            return

        if event.msg.startswith(".module load"):
            self.bot.logger.write(
                Logger.INFO,
                " loading " +
                event.msg.split()[2] +
                "...",
                self.bot.NICK)
            retval = self.load(event.msg.split()[2])
            if retval == 0:
                self.bot.logger.write(
                    Logger.INFO, " loaded " + event.msg.split()[2])
                self.bot.brain.notice(
                    event.channel, "loaded " + event.msg.split()[2])
            elif retval == 2:
                self.bot.logger.write(
                    Logger.INFO,
                    " load failed; " +
                    event.msg.split()[2] +
                    " is already loaded")
                self.bot.brain.notice(
                    event.channel,
                    "load failed; " +
                    event.msg.split()[2] +
                    " is already loaded")
            else:
                self.bot.logger.write(
                    Logger.WARNING,
                    " failed to load " +
                    event.msg.split()[2],
                    self.bot.NICK)
                self.bot.brain.notice(
                    event.channel,
                    "failed to load " +
                    event.msg.split()[2])

        if event.msg == ".module eventslist":
            events_set = set()
            for m in self.bot.events_list:
                events_set.add(m._type)
            message = ""
            for s in sorted(events_set):
                message += s + ", "
            # needs newline at the end, and we remove the final comma
            self.say(event.user, message[:-2] + '\n')

        if event.msg.startswith(".module list"):
            # the set prevents a module with multiple events being printed more
            # than once
            modules_set = set()
            for m in self.bot.events_list:
                for s in m.subscribers:
                    modules_set.add(s.__class__.__name__)

            message = ""
            for s in sorted(modules_set):
                message += s + ", "
            # needs newline at the end, and we remove the final comma
            self.say(event.user, message[:-2] + '\n')
            return

        if event.msg.startswith(".module unload"):
            if self.unload(event.msg.split()[2]):
                self.printer(
                    "NOTICE " +
                    event.channel +
                    " :unloaded " +
                    event.msg.split()[2] +
                    '\n')
            else:
                self.printer(
                    "NOTICE " +
                    event.channel +
                    " :failed to unload " +
                    event.msg.split()[2] +
                    '\n')

        """careful here: XXX - unloading looks it up by class name, and the bot's loading module looks it up by filename
    - this can lead to situations where you just reload a module over and over instead of unloading it
    because the module name and class name differ """
        if event.msg.startswith(
                ".module reload"):  # perform both unloading and reloading
            # first unload
            for m in self.bot.events_list:
                for s in m.subscribers:
                    try:
                        if event.msg.split()[2].lower(
                        ) == s.__class__.__name__.lower():
                            #self.printer("NOTICE " + event.channel + " :unloaded " + event.msg.split()[2] + '\n')
                            # the events themselves hold onto the subscribing
                            # modules, so just remove that one.
                            m.subscribers.remove(s)
                    except IndexError:
                        return
            # then load
            #self.bot.logger.write(Logger.INFO, " loading " + event.msg.split()[2] + "...")
            retval = self.load(event.msg.split()[2])
            if retval == 0:
                self.bot.logger.write(
                    Logger.INFO,
                    " reloaded " +
                    event.msg.split()[2],
                    self.bot.NICK)
                self.bot.brain.notice(
                    event.channel, "reloaded " + event.msg.split()[2])
            else:
                self.bot.logger.write(
                    Logger.WARNING,
                    " failed to reload " +
                    event.msg.split()[2],
                    self.bot.NICK)
                self.bot.brain.notice(
                    event.channel,
                    "failed to reload " +
                    event.msg.split()[2])

        if event.msg.startswith(".module eventdelete"):
            if self.unload_event(event.msg.split()[2]):
                self.bot.brain.notice(
                    event.channel,
                    " removed event " +
                    event.msg.split()[2])

    def unload_event(self, eventname):
        try:
            for e in self.bot.events_list:
                if eventname == e._type:
                    self.bot.events_list.remove(e)
                    return True
        except BaseException:
            return False
        return False

    def unload(self, modulename):
        unloaded_successfully = False
        for m in self.bot.events_list:
            for s in m.subscribers:
                if modulename == s.__class__.__name__.lower():
                    # the events themselves hold onto the subscribing modules,
                    # so just remove that one.
                    m.subscribers.remove(s)
                    unloaded_successfully = True
        return unloaded_successfully

    def load(self, modulename):
        # this may seem redundant, but modules may become unloaded in between
        # calls.
        modules_set = set()
        for m in self.bot.events_list:
            for s in m.subscribers:
                modules_set.add(s.__class__.__name__.lower())

        if modulename in modules_set:
            return 2

        return self.bot.load_modules(specific=modulename)
