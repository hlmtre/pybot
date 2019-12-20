class BaseModule(object):
  """
  A base module class for deriving modules (anything you fine folk write, probably) to inherit from.
  The nice this is this allows you to define your own post_init and handle functions.

  In your module's post_init, define and register your own events, and pass your module in.

  .. code-block:: python

    def MyModule(BaseModule):
      def post_init(self):
        e = Event("__wee__")
        e.define("foo")
        self.bot.register_event(e,self)


  Bam, you've got the things you need (a bot handle, mostly) and by extending BaseModule you implement the right things to be called without error.
  Elzar.
  """
  def __init__(self, events=None, printer_handle=None, bot=None, say=None):
    """
    This is called by load_modules for every .py in the modules directory. Your module must implement this, one way or the other, either directly,
    by implementing this function signature, or indirectly, by inheriting from BaseModule. I suggest the latter.
    """
    self.events = events
    self.printer = printer_handle
    self.interests = []
    self.bot = bot
    self.say = say

    # IMPORTANT: you must subscribe to events before you add your own below, or you'll subscribe twice.
    # register ourself for any events that we're interested in that exist already
    for e in events:
      if e._type in self.interests:
        e.subscribe(self)

    self.help = None

    self.post_init()

  def handle(self, event):
    pass

  def post_init(self):
    """
    Called after init is set up and builds out our basic module's needs. Allows you to do your own post-processing when inheriting from BaseModule.
    """
