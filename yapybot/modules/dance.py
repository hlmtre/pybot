class Dance:
  def __init__(self, events=None, printer_handle=None, bot=None, say=None):
    self.events = events
    self.printer = printer_handle
    self.interests = ['__.dance__']
    self.bot = bot 

    self.help = ".dance"

    for event in events:
      if event._type in self.interests:
        event.subscribe(self)

  def handle(self, event):
    try:
      self.printer("PRIVMSG " + event.channel + " : :D-\-< " + '\n')
      self.printer("PRIVMSG " + event.channel + " : :D-|-< " + '\n')
      self.printer("PRIVMSG " + event.channel + " : :D-/-< " + '\n')
    except TypeError:
      pass
