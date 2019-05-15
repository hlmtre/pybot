import sys
import time
from datetime import datetime, timedelta
from event import Event
try:
  if sys.version_info > (3, 0, 0):
    from .basemodule import BaseModule
  else:
    from basemodule import BaseModule
except (ImportError, SystemError):
  from modules.basemodule import BaseModule

class Uptime(BaseModule):
  def post_init(self):
    uptime_event = Event("__.uptime__")
    uptime_event.define(msg_definition="^\.uptime")
    uptime_event.subscribe(self)
    self.help = ".uptime (spits out uptime)"
    # register ourself to our new custom event
    self.bot.register_event(uptime_event, self)

    starttime = time.time()
    localtime = time.localtime()

    if 'uptime' not in self.bot.mem_store:
      self.bot.mem_store['uptime'] = dict()
      self.bot.mem_store['uptime']['localtime'] = localtime
      self.bot.mem_store['uptime']['starttime'] = starttime

  def handle(self, event):
    self._uptime(event.channel)

  def _uptime(self, channel):
    #print timedelta(seconds=time.time() - self.starttime)
    self.say(channel,"I've been up " +str(timedelta(seconds=time.time() - self.bot.mem_store['uptime']['starttime'])).split(".")[0] + ", since "+time.strftime("%a, %d %b %Y %H:%M:%S -0800", self.bot.mem_store['uptime']['localtime']))
