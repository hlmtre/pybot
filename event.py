import re
class Event:
  def __init__(self, _type):
    self._type = _type
    self.subscribers = list()
    self.user = ""
    self.definition = ""
    self.channel = ""
    
  def subscribe(self, e):
    self.subscribers.append(e)

  def define(self, string):
    self.definition = string

  def matches(self, line):
    if re.search(self.definition, line):
      return True
    return False

  def notifySubscribers(self, line):
    self.user = line.split(":")[1].rsplit("!")[0] # nick is first thing on line
    self.channel = line.rsplit(":"[-1]) # channel user joined is last
    for s in self.subscribers:
      s.handle(self)
