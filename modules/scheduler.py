from datetime import datetime, timezone, timedelta
import time
import sys
from event import Event

from pytimeparse import parse

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


class Sched(BaseModule):
  def post_init(self):
    sched = Event("__.schedule__")
    sched.define(msg_definition="^\.schedule")
    sched.subscribe(self)
    self.help = ".schedule in <1m|5h|32s|etc> say <#channel> <phrase>"
    self.cmd = ".schedule"

    # register ourself to our new sched event
    self.bot.register_event(sched, self)

  def handle(self, event):
    if event.msg.startswith(".schedule"):
      try:
        split = event.msg.split()
        if len(split) <= 6:
          self.error(event.channel)
          return
        chan = split[4]
        message = ' '.join(split[5:])
        delay = split[2]
        send_time = datetime.now(timezone.utc)
        td = timedelta(seconds=parse(delay))
        target = send_time + td
        if not chan.startswith("#"):
          self.say(event.channel, "invalid channel.")
          return
        self.bot.scheduler.schedule_task(chan, message, event.user, trigger_delay=delay, source_channel=event.channel)
        self.say(event.channel, "registered event for channel " + chan + " at " + str(target) + " UTC.")
      except IndexError:
        self.error(event.channel)
        return

  def error(self, channel):
    self.say(channel, "u guf ur furmat")
