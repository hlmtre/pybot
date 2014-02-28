import re
class Event:
  def __init__(self, _type):
    self._type = _type
    self.subscribers = list() # this is a list of subscribers to notify
    self.user = ""
    self.definition = ""
    self.channel = ""
    self.line = ""
    self.msg = ""
    
  def subscribe(self, e):
    self.subscribers.append(e)

  def define(self, string):
    self.definition = string

  def matches(self, line):
    if re.search(self.definition, line):
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
    for e in l:
      if e.startswith("#"):
        self.channel = e
        break
    for s in self.subscribers:
      s.handle(self)
