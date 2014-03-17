from event import Event
class BaseModule(object):
  def __init__(self, events=None, printer_handle=None, bot=None, say=None):
    self.events = events
    self.printer = printer_handle
    self.interests = []
    self.bot = bot
    self.say = say

    # IMPORTANT: you must subscribe to events before you add your own below, or you'll subscribe twice.
    # register ourself for any events that we're interested in that exist already
    for event in events:
      if event._type in self.interests:
        event.subscribe(self)

    self.help = None

    self.post_init()

  def handle(self, event):
    pass

  def post_init(self):
    pass
