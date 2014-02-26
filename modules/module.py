class Module:
  def __init__(self, events=None, printer_handle=None, bot=None):
    self.events = events
    self.printer = printer_handle
    self.bot = bot
    self.interests = ['__module__']
    for event in events:
      if event._type in self.interests:
       # print "DEBUG: registering to ",
       # print event
        event.subscribe(self)

  def handle(self, event):
    if event.msg.startswith(".module load"):
      retval = self.load(event.msg.split()[2])
      if retval == 0:
        self.printer("PRIVMSG " + event.channel + " :loaded " + event.msg.split()[2] + '\n')
      else:
        self.printer("PRIVMSG " + event.channel + " :failed to load " + event.msg.split()[2] + '\n')
        
       

    if event.msg.startswith(".module list"):
      for m in self.bot.events_list:
        for s in m.subscribers:
          print s.__class__.__name__
      return


    if event.msg.startswith(".module unload"):
      if self.bot.conf.getOwner(self.bot.network) == event.line.split()[0].split("!",1)[0].replace(":",""):
        for m in self.bot.events_list:
          for s in m.subscribers:
            if event.msg.split()[2].lower() == s.__class__.__name__.lower():
              self.printer("PRIVMSG " + event.channel + " :removing " + event.msg.split()[2] + '\n')
              m.subscribers.remove(s)
        return

  def load(self, modulename):
    return self.bot.load_modules(specific=modulename)
