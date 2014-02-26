class Example:
  def __init__(self, events=None, printer_handle=None, bot=None):
    self.events = events
    self.printer = printer_handle
    self.interests = ['__joins__']
    for event in events:
      if event._type in self.interests:
       # print "DEBUG: registering to ",
       # print event
        event.subscribe(self)

  def handle(self, event):
    try:
      self.printer("PRIVMSG " + event.channel + " :welcome, " + event.user + '\n')
    except TypeError:
      print "DEBUG: TypeError: ",
      print event.channel,
      print event.user

