from event import Event
import ast
try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule
class Debugger(BaseModule):
  def post_init(self):
    debug_event = Event("__.debug__")
    debug_event.define(msg_definition="^\.debug")
    debug_event.subscribe(self)

    # register ourself to our new debug_event event
    self.bot.register_event(debug_event, self)

  def recurse(self, obj):
    if type(obj) is not dict:
      print obj
    else:
      for k in obj:
        self.recurse(k)

  def pretty(self, d, event, indent=0):
    for key, value in d.iteritems():
      self.say(event.user, '\t' * indent + key.encode('utf-8','ignore'))
      if isinstance(value, dict):
        pretty(value, event, indent+1)
      else:
        try:
          self.say(event.user, '\t' * (indent+1) + str(value))
        except: 
          self.say(event.user,'\t' * (indent+1) + value.encode('utf-8','ignore'))
    
  def handle(self, event):
    try:
      key = event.msg.split()[1]
      keyslist = []
      for thing in event.msg.split()[1:]:
        keyslist.append(thing)
        #print self.bot.mem_store[thing]

      if len(keyslist) > 1:
        neststring = ""
        for k in keyslist:
          neststring = neststring+'[\''+k+'\']'
        print neststring

      self.pretty(self.bot.mem_store[key], event)
        # HIGHLY insecure; TODO
        #self.pretty(self.bot.mem_store[eval(neststring)])
        
      #print self.bot.mem_store['qdb']['#fg']
#      outstr = ", ".join(self.bot.mem_store[key])
#      self.say(event.user, outstr)
    except IndexError:
      print "ERROR: "
      print event.msg
