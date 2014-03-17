class Pimp:
  def __init__(self, events=None, printer_handle=None, bot=None, say=None):
    self.events = events
    self.printer = printer_handle
    self.interests = ['__pimp__']

    self.cmd = ".pimp"
    self.help = None

    for event in events:
      if event._type in self.interests:
        event.subscribe(self)

  def handle(self, event):
    try:
      self.printer("PRIVMSG " + event.channel + " : http://bits.zero9f9.com/pybot" + '\n')
    except TypeError:
      print "DEBUG: TypeError: ",
      print event.channel,
      print event.user
    except:
      print "AIIIYEEEE"
