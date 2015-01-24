try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule

class EventTracker(BaseModule):
  def post_init(self):
    for event in self.events:
      event.subscribe(self)

  def handle(self, event):
    print "saw " + event._type + " on line " + event.msg + " from server"
