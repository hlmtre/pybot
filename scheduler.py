# -*- coding: utf-8 -*-
import datetime
import timezone
import time

class Scheduler (threading.Thread):
  class Task():
    def __init__(self, channel, message, sender, trigger_time=None, trigger_delay=None, send_time=None):
      self.channel = channel
      self.message = message
      self.sender = sender
      self.send_time = send_time
      self.trigger_delay = trigger_delay
      self.trigger_time = trigger_time

  def __init__(self, parent_bot):
    self.parent_bot = parent_bot
    self.task_list = []

  def run(self):
    self.poll()

  def poll(self):
    now = datetime.now(timezone.utc)
    for t in self.task_list:
      if now > t.trigger_time:
        self.task_list.remove(t)
        self.trigger(t)
    time.sleep(10)

  def register_task(self, channel, message, sender, trigger_time=None, trigger_delay=None, send_time=None):
    t = Task(channel, message, sender, trigger_time, trigger_delay, send_time)
    self.task_list.append(t)

  def trigger(self, task):
    self.bot.say(task.channel, task.message)
