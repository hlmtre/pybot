from event import Event
class BaseModule(object):
  """
  A base module class for deriving modules (anything you fine folk write, probably) to inherit from.
  The nice this is this allows you to define your own post_init and handle functions.

  In your module's post_init, define and register your own events, and pass your module in.
  
  .. code-block:: python

    def post_init(self):
      e = Event("_wee__")
      e.define("foo")
      self.bot.register_event(e,self)


  Bam, you've got the things you need (a bot handle, mostly) and you implement the right things to be called without error.
  Elzar.
  """
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
