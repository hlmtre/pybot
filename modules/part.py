class Part:
  def __init__(self, events=None, printer_handle=None, bot=None):
    self.events = events
    self.printer = printer_handle
    self.interests = ['__.part__']
    self.bot = bot

    self.cmd = None
    self.help = None

    for event in events:
      if event._type in self.interests:
        event.subscribe(self)

  def handle(self, event):
    try:
      if self.bot.conf.getOwner(self.bot.network) == event.line.split()[0].split("!",1)[0].replace(":","") and event.line.split()[2] == self.bot.conf.getNick(self.bot.network):
        self.bot.send("PART " + event.line.split()[4] + '\n')
    except:
      pass
          

