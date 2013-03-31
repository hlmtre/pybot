"""
  modules get a list of events to subscribe to.
"""
class Example:
  def __init__(self, events, printer_handle):
    self.events = events
    self.printer = printer_handle
    self.interests = ['__joins__']
    for event in events:
      if event._type in self.interests:
        self.register(event)

  def register(self, event):
    event.subscribe(self)

  def handle(self, event):
    self.printer("PRIVMSG " + event.channel + " welcome, " + event.user + '\n')

