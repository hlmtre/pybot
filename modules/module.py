class Module:
  def __init__(self, events=None, printer_handle=None, bot=None):
    self.events = events
    self.printer = printer_handle
    self.bot = bot
    self.interests = ['__module__']
    for event in events:
      if event._type in self.interests:
        event.subscribe(self)

  def handle(self, event):
    if not self.bot.conf.getOwner(self.bot.network) == event.line.split()[0].split("!",1)[0].replace(":",""):
      return

    if event.msg.startswith(".module load"):
      retval = self.load(event.msg.split()[2])
      if retval == 0:
        self.printer("NOTICE " + event.channel + " :loaded " + event.msg.split()[2] + '\n')
      else:
        self.printer("NOTICE " + event.channel + " :failed to load " + event.msg.split()[2] + '\n')

    if event.msg.startswith(".module list"):
      for m in self.bot.events_list:
        for s in m.subscribers:
          print s.__class__.__name__
      return

    if event.msg.startswith(".module unload"):
      for m in self.bot.events_list:
        for s in m.subscribers:
          if event.msg.split()[2].lower() == s.__class__.__name__.lower():
            self.printer("NOTICE " + event.channel + " :unloaded " + event.msg.split()[2] + '\n')
            # the events themselves hold onto the subscribing modules, so just remove that one.
            m.subscribers.remove(s)
      return

  def load(self, modulename):
    return self.bot.load_modules(specific=modulename)
