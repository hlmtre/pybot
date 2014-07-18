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
    
  def subscribe(self, e):
    self.subscribers.append(e)

  def define(self, definition=None, msg_definition=None, user_definition=None):
    if definition is not None:
      self.definition = definition
    if msg_definition is not None:
      self.msg_definition = msg_definition
    if user_definition is not None:
      self.user_definition = user_definition

  def matches(self, line):
    try:
      msg = line.split(":",2)[2]
    except IndexError:
      msg = ""

    if len(self.msg_definition) > 0:
      if re.search(self.msg_definition, msg):
        return True

    if len(self.definition) > 0:
      if re.search(self.definition, line):
        return True

    if len(self.user_definition) > 0:
      if len(line) and "PRIVMSG" in line > 0:
        line_array = line.split()
        user_and_mask = line_array[0][1:]
        user = user_and_mask.split("!")[0]
        if self.user_definition == user:
          return True

    return False

  def notifySubscribers(self, line):
    self.line = line
    self.user = line.split(":")[1].rsplit("!")[0] # nick is first thing on line
    # we're on a function line - JOIN, PART, etc
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
