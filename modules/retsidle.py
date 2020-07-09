# -*- coding: utf-8 -*-
import sys
import datetime

from collections import deque
from time import sleep
from event import Event

import util

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

"""
WHOIS mech
:irc.zero9f9.com 311 telnmtre mech mech Clk-8576552F.members.linode.com * :Bangarang Cunterbug
:irc.zero9f9.com 319 telnmtre mech :@#bots3 #fg #development @#bots2 #bots #bot-dev
:irc.zero9f9.com 312 telnmtre mech irc.zero9f9.com :09f9 IRC Server
# server        msg_id asker  askee idle  login
:irc.zero9f9.com 317 telnmtre mech 15101 1590381020 :seconds idle, signon time
:irc.zero9f9.com 318 telnmtre mech :End of /WHOIS list.
"""

class Retsidle(BaseModule):

  def post_init(self):
    retse = Event("__.retsidle__")
    retse.define(msg_definition="^\.retsidle")
    retse.subscribe(self)
    self.cmd = ".retsidle"
    self.help = "How long has rets been idle?"
    self.rets_current_nick = "rets|audrey"

    self.bot.register_event(retse, self)

  def handle(self, event):
    self.bot.bare_send("WHOIS " + self.rets_current_nick)
    idle_time = 0
    for line in list(self.bot.recent_lines):
      try:
        if int(util.parse_line(line).message_number) == 317:
          idle_time = int(line.split()[4])
      except:
        pass

    #print(idle_time)
    since = datetime.datetime.now() - datetime.timedelta(seconds=idle_time)
    self.say(event.channel, self.rets_current_nick +
             " has been idle since " + since.strftime("%Y-%m-%d %H:%M:%S"))
