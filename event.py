import re
class Event:
  """
  Allows event type definition. The definition accepts a regex.
  Every event can be triggered by specific lines, messages, message_id or users.
  Eventually (see time_event branch for proof-of-concept implementation) time-sensitive events will be triggerable as well.

  Each line received by the bot is passed to each module in the modules_list. If the module determines the line matches what the event cares about,
  the event calls each of its subscribers itself, which contains all the information the module needs to respond appropriately.

  To use:

  .. code-block:: python

    e = Event("__my_type__")
    e.define("some_regex")
    bot.register_event(e, calling_module)

  """
  def __init__(self, _type):
    """
    Define your own type here. Make sure if you're making a broad event (all messages, for example) you use a sane type, as other modules that care about this kind of event can subscribe to it.
    
    Args:
    _type: string. like "__youtube__" or "__weather__". Underscores are a convention.
    """
    self._type = _type
    self.subscribers = list() # this is a list of subscribers to notify
    self.user = ""
    self.definition = ""
    self.msg_definition = ""
    self.user_definition = ""
    self.channel = ""
    self.line = ""
    self.msg = ""
    self.verb = ""
    self.is_pm = False
    self.message_id = -1
    self.time_event = False
    
  def subscribe(self, e):
    """
    Append passed-in event to our list of subscribing modules.

    Args:
    e: event.
    """
    self.subscribers.append(e)

  def define(self, definition=None, msg_definition=None, user_definition=None, message_id=None, time_event=False):
    """
    Define ourself by general line (definition), msg_definition (what someone says in a channel or PM), user_definition (the user who said the thing), or message_id (like 376 for MOTD or 422 for no MOTD)
    Currently, an event is defined by only one type of definition. If one were to remove the returns after each self. set, an event could be defined and triggered by any of several definitions.

    Args:
    definition: string. regex allowed.
    msg_definition: string. regex allowed. this is what someone would say in a channel. like "hello, pybot".
    user_definition: string. the user that said the thing. like 'hlmtre' or 'BoneKin'.
    message_id: the numerical ID of low-level IRC protocol stuff. 376, for example, tells clients 'hey, this is the MOTD.'
    time_event: boolean. if this is a timed event, the other definitions are irrelevant.
    """
    if time_event is not False:
      self.time_event = True
      return
    if definition is not None:
      self.definition = definition
      return
    if msg_definition is not None:
      self.msg_definition = msg_definition
      return
    if user_definition is not None:
      self.user_definition = user_definition
      return
    if message_id is not None:
      self.message_id = message_id
      return

  def matches(self, line):
    """
    Fills out the event object per line, and returns True or False if the line matches one of our definitions.
    Args:
    line: string. The entire incoming line.

    Return:
    boolean; True or False.
    """
    # perhaps TODO
    # first try very simply
    if len(self.definition) and self.definition in line:
      return True
    # grab message id. not always present
    try:
      temp = line.split(":")[1].split(" ")[1]
    except IndexError:
      pass

    try:
      message_id = int(temp)
    except (ValueError, UnboundLocalError):
      message_id = 0

    try:
      msg = line.split(":",2)[2]
    except IndexError:
      return

    if len(self.msg_definition):
      if re.search(self.msg_definition, msg):
        return True

    if len(self.definition):
      if re.search(self.definition, line):
        return True

    if len(self.user_definition):
      if len(line) and "PRIVMSG" in line > 0:
        line_array = line.split()
        user_and_mask = line_array[0][1:]
        user = user_and_mask.split("!")[0]
        if self.user_definition == user:
          return True

    if type(self.message_id) is int:
      if self.message_id == message_id:
        return True

    return False

  def time_notify_subscribers(self):
    for s in self.subscribers:
      # horrible kludge. this feels so dirty.
      if s.time_since >= int(round(s.time_delta/2) - 1):
        s.time_since = 0
        s.handle(self)
      else:
        s.time_since += 1
    

  def notifySubscribers(self, line):
    """
    Fills out the object with all necessary information, then notifies subscribers with itself (an event with all the line information parsed out) as an argument.
    Args:
    line: string
    
    """
    self.line = line
    self.user = line.split(":")[1].rsplit("!")[0] # nick is first thing on line
    if "JOIN" in line or "QUIT" in line:
      self.user = line.split("!")[0].replace(":","")
    try:
      temp = line.split(":")[1].split(" ")[1]
    except IndexError:
      pass

    try:
      self.msg = line.split(":",2)[2]
    except IndexError:
      self.msg = ""

    l = line.split()
    self.channel = ""
    self.verb = ""
    ind = 0
    privmsg_index = 0
    for e in l:
      ind+=1
      if e == "PRIVMSG":
        privmsg_index = ind
      if e.startswith("#"):
        self.channel = e
        break
    for v in l:
      if v in ["JOIN","PART","QUIT","NICK","KICK","PRIVMSG","TOPIC", "NOTICE", "PING", "PONG", "MODE"]:
        self.verb = v
        break
    # our channel is the next one from PRIVMSG
    if self.verb == "PRIVMSG" and not l[privmsg_index].startswith("#"):
      self.is_pm = True
    for s in self.subscribers:
      s.handle(self)
