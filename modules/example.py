from event import Event
class Example:
  def __init__(self, events=None, printer_handle=None, bot=None):
    self.events = events
    self.printer = printer_handle
    self.interests = ['__joins__']
    self.bot = bot

    # IMPORTANT: you must subscribe to events before you add your own below, or you'll subscribe twice.
    # register ourself for any events that we're interested in that exist already
    for event in events:
      if event._type in self.interests:
        event.subscribe(self)

    custom = Event("__cusom__")
    custom.define("some_regex_here")
    custom.subscribe(self)

    # register ourself to our new custom event
    self.bot.register_event(custom, self)

    self.help = None

  def handle(self, event):
    try:
      self.printer("PRIVMSG " + event.channel + " :welcome, " + event.user + '\n')
    except TypeError:
      print "DEBUG: TypeError: ",
      print event.channel,
      print event.user

