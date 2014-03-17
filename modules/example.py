from event import Event
class Example:
  def __init__(self, events=None, printer_handle=None, bot=None, say=None):
    self.events = events
    self.printer = printer_handle
    self.interests = ['__custom__']
    self.bot = bot
    self.say = say

    # IMPORTANT: you must subscribe to events before you add your own below, or you'll subscribe twice.
    # register ourself for any events that we're interested in that exist already
    for event in events:
      if event._type in self.interests:
        event.subscribe(self)

    custom = Event("__custom__")
    custom.define("some_regex_here")
    custom.subscribe(self)

    # register ourself to our new custom event
    self.bot.register_event(custom, self)

    self.help = None

  def handle(self, event):
    self.say(event.channel, "welcome, " + event.user)
    #self.printer("PRIVMSG " + event.channel + " :welcome, " + event.user + '\n')

