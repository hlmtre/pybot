import sys
from event import Event

if sys.version_info > (3, 0, 0):
  try:
    from .basemodule import BaseModule
  except (ImportError, SystemError):
    from modules.basemodule import BaseModule
else:
  try:
    from basemodule import BaseModule
  except (ImportError, SystemError):
    from modules.basemodule import BaseModule

class Debugger(BaseModule):
  def post_init(self):
    debug_event = Event("__.debug__")
    debug_event.define(msg_definition="^\.debug")
    debug_event.subscribe(self)

    delete_event = Event("__.delete__")
    delete_event.define(msg_definition="^\.delete")
    delete_event.subscribe(self)

    # register ourself to our new debug_event event
    self.bot.register_event(debug_event, self)
    self.bot.register_event(delete_event, self)

  def recurse(self, obj):
    if type(obj) is not dict:
      print(obj)
    else:
      for k in obj:
        self.recurse(k)

  def mem_store_delete(self, mem_store_key):
    if not mem_store_key:
      return False
    if mem_store_key in self.bot.mem_store:
      del(self.bot.mem_store[mem_store_key])
      return True

  def pretty(self, d, event, indent=0):
    for key, value in d.items():
      if sys.version_info > (3, 0, 0):
        self.say(event.user, '\t' * indent + key)
      else:
        self.say(event.user, '\t' * indent + key.encode('utf-8','ignore'))
      if isinstance(value, dict):
        self.pretty(value, event, indent+1)
      else:
        try:
          self.say(event.user, '\t' * (indent+1) + str(value))
        except:
          self.say(event.user,'\t' * (indent+1) + value.encode('utf-8','ignore'))

  def handle(self, event):
    if not self.bot.brain._isAdmin(event.user):
      return
    if event.msg.startswith(".delete"):
      target = event.msg.split()[-1]
      if self.mem_store_delete(target):
        self.say(event.user, "deleted " + target + " from mem_store")
      return
    try:
      key = event.msg.split()[1]
      keyslist = []
      for thing in event.msg.split()[1:]:
        keyslist.append(thing)
      #  print self.bot.mem_store[thing]

      if len(keyslist) > 1:
        neststring = ""
        for k in keyslist:
          neststring = neststring+'[\''+k+'\']'
      #  print neststring

      try:
        self.pretty(self.bot.mem_store[key], event)
      except KeyError:
        self.say(event.user, "no key by name " + key)
        # HIGHLY insecure; TODO
        #self.pretty(self.bot.mem_store[eval(neststring)])

      #print self.bot.mem_store['qdb']['#fg']
#      outstr = ", ".join(self.bot.mem_store[key])
#      self.say(event.user, outstr)
    except IndexError:
      print("ERROR: ")
      print(event.msg)
