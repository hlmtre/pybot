from logger import Logger
from event import Event
class Module:
  def __init__(self, events=None, printer_handle=None, bot=None, say=None):
    self.events = events
    self.printer = printer_handle
    self.bot = bot
    self.interests = []

    self.cmd = None
    self.help = None

    mod = Event("__.module__")
    mod.define(msg_definition="^\.module ")
    mod.subscribe(self)

    self.bot.register_event(mod, self)

    #for event in events:
    #  if event._type in self.interests:
    #    event.subscribe(self)

  def handle(self, event):
    #if not self.bot.conf.getOwner(self.bot.network) == event.user:
    if not self.bot.brain._isAdmin(event.user):
      return

    if event.msg.startswith(".module load"):
      self.bot.logger.write(Logger.INFO, " loading " + event.msg.split()[2] + "...", self.bot.NICK)
      retval = self.load(event.msg.split()[2])
      if retval == 0:
        self.bot.logger.write(Logger.INFO, " loaded " + event.msg.split()[2])
        self.bot.brain.notice(event.channel, "loaded " + event.msg.split()[2])
      elif retval == 2:
        self.bot.logger.write(Logger.INFO, " load failed; " + event.msg.split()[2] + " is already loaded")
        self.bot.brain.notice(event.channel, "load failed; " + event.msg.split()[2] + " is already loaded")
      else:
        self.bot.logger.write(Logger.WARNING, " failed to load " + event.msg.split()[2], self.bot.NICK)
        self.bot.brain.notice(event.channel, "failed to load " + event.msg.split()[2])

    if event.msg == ".module eventslist":
      for m in self.bot.events_list:
        print m._type

    if event.msg.startswith(".module list"):
      # the set prevents a module with multiple events being printed more than once
      modules_set = set()
      for m in self.bot.events_list:
        for s in m.subscribers:
          modules_set.add(s.__class__.__name__)

      print modules_set
      return

    if event.msg.startswith(".module unload"):
      for m in self.bot.events_list:
        for s in m.subscribers:
          if event.msg.split()[2].lower() == s.__class__.__name__.lower():
            self.printer("NOTICE " + event.channel + " :unloaded " + event.msg.split()[2] + '\n')
            # the events themselves hold onto the subscribing modules, so just remove that one.
            m.subscribers.remove(s)
      return

    if event.msg.startswith(".module reload"): # perform both unloading and reloading
      # first unload
      for m in self.bot.events_list:
        for s in m.subscribers:
          if event.msg.split()[2].lower() == s.__class__.__name__.lower():
            #self.printer("NOTICE " + event.channel + " :unloaded " + event.msg.split()[2] + '\n')
            # the events themselves hold onto the subscribing modules, so just remove that one.
            m.subscribers.remove(s)
      # then load
      #self.bot.logger.write(Logger.INFO, " loading " + event.msg.split()[2] + "...")
      retval = self.load(event.msg.split()[2])
      if retval == 0:
        self.bot.logger.write(Logger.INFO, " reloaded " + event.msg.split()[2], self.bot.NICK)
        self.bot.brain.notice(event.channel, "reloaded " + event.msg.split()[2])
      else:
        self.bot.logger.write(Logger.WARNING, " failed to reload " + event.msg.split()[2], self.bot.NICK)
        self.bot.brain.notice(event.channel, "failed to reload " + event.msg.split()[2])
      

  def load(self, modulename):
# this may seem redundant, but modules may become unloaded in between calls.
    modules_set = set()
    for m in self.bot.events_list:
      for s in m.subscribers:
        modules_set.add(s.__class__.__name__.lower())

    if modulename in modules_set:
      return 2

    return self.bot.load_modules(specific=modulename)
