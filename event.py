import re
class Event:
  def __init__(self, _type):
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
    
  def subscribe(self, e):
    self.subscribers.append(e)

  def define(self, definition=None, msg_definition=None, user_definition=None, message_id=None):
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

  def notifySubscribers(self, line):
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
