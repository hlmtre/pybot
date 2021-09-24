# -*- coding: utf-8 -*-
from datetime import datetime, timezone, timedelta
from time import sleep
import threading

from pytimeparse import parse


class Scheduler (threading.Thread):
    FREQUENCY = 1

    class Task():
        def __init__(self, channel, message, sender,
                     trigger_time=None, trigger_delay=None, send_time=None):
            self.channel = channel
            self.message = message
            self.sender = sender
            self.send_time = send_time
            self.trigger_delay = trigger_delay
            self.trigger_time = trigger_time

    def __init__(self, parent_bot):
        threading.Thread.__init__(self)
        self.parent_bot = parent_bot
        self.task_list = []

    def run(self):
        self._poll()

    def _poll(self):
        while True:
            if self.parent_bot.DEBUG:
                self.parent_bot.debug_print(
                    "polling " + str(len(self.task_list)) + " tasks...")
            now = datetime.now(timezone.utc)
            for t in self.task_list:
                if t.trigger_delay is not None and now > t.trigger_delay:
                    self.trigger(t)
                    self.task_list.remove(t)
                if t.trigger_time is not None and now > t.trigger_time:
                    self.trigger(t)
                    self.task_list.remove(t)
            sleep(Scheduler.FREQUENCY)

    def schedule_task(self, channel, message, sender, trigger_time=None,
                      trigger_delay=None, send_time=None, source_channel=None):
        if self.parent_bot.DEBUG:
            self.parent_bot.debug_print(
                'registering task: ' + channel + ' ' + message + ' ' + sender)
        send_time = datetime.now(timezone.utc)
        if trigger_delay is not None:
            td = timedelta(seconds=parse(trigger_delay))
            trigger_delay = send_time + td
        t = self.Task(
            channel,
            message,
            sender,
            trigger_time,
            trigger_delay,
            send_time)
        self.task_list.append(t)

    def trigger(self, task):
        self.parent_bot.say(task.channel, task.message)
