from datetime import datetime, timezone, timedelta
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


class Schedule(BaseModule):
    def post_init(self):
        sched = Event("__.schedule__")
        sched.define(msg_definition="^\\.schedule")
        sched.subscribe(self)
        self.help = ".schedule in <1m|5h|32s|1w3d2h32m|etc> say <#channel> <phrase>. accepted units are s, m, h, and w (seconds, minutes, hours, and weeks)."
        self.help += "\n .schedulelist <channelname>"
        self.help += "\n example: .schedule in 30m say #fg remember to turn off the oven"
        self.help += "\n example: .schedulelist #fg"
        self.cmd = ".schedule"

        # register ourself to our new sched event
        self.bot.register_event(sched, self)

    def handle(self, event):
        if event.msg.startswith(".schedulelist"):
            self.bot.scheduler.list_schedules(event.msg.split()[1], event.channel)
            return
        if event.msg.startswith(".schedule"):
            try:
                split = event.msg.split()
                if len(split) < 6:
                    self.error(event.channel)
                    return
                chan = split[4]
                message = ' '.join(split[5:])
                delay = split[2]
                send_time = datetime.now(timezone.utc)
                td = timedelta(seconds = 0)
                try:
                    seconds = parse(delay)
                except Exception as e:
                    print(e.message)
                    self.say(event.channel, "time parsing error. accepted units: seconds (s), minutes (m), hours (h), and weeks (w).")
                    return
                try:
                    td = timedelta(seconds=seconds)
                except TypeError as e:
                    print(e.message)
                    self.say(event.channel, "time parsing error. accepted units: seconds (s), minutes (m), hours (h), and weeks (w).")
                    return
                target = send_time + td
                if not chan.startswith("#"):
                    self.say(event.channel, "invalid channel.")
                    return
                self.bot.scheduler.schedule_task(
                    chan, message, event.user, trigger_delay=delay, source_channel=event.channel)
                self.say(event.channel, "registered event for channel " +
                         chan + " at " + str(target)[:-13] + " UTC.")
            except IndexError:
                self.error(event.channel)
                return

    def error(self, channel):
        self.say(channel, "u guf ur furmat")
