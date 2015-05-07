# -*- coding: utf-8 -*-

from event import Event
import random

try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule
class KanboModule(BaseModule):
  def post_init(self):
    kanbo = Event("__.custom__")
    kanbo.define(msg_definition="^\.kanbo")
    kanbo.subscribe(self)

    self.bot.register_event(kanbo, self)
    self.messages = [u'( ͡° ͜ʖ ͡°)', 'i am kanbo, watch me disobey simple and direct instruction']
    
  def handle(self, event):
    self.say(event.channel, random.choice(self.messages))
