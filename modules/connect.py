import json

from bot import Bot
from confman import ConfManager
from event import Event
try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule

class Connect(BaseModule):
  def post_init(self):
    connect = Event("__.connect__")
    connect.define(msg_definition="^\.connect")
    connect.subscribe(self)

    self.cmd = '.connect <servername> <channelname> <port> <password (optional)>'
    self.help = self.cmd

    self.bot.register_event(connect, self)

    self.CONF_STRING = '{ "__pybot_conf":{ "db_type": "%s" }, "%s": '
    self.CONF_STRING += '{ "channels": [ "%s" ], "port":"%s", "nick": "%s","ircpass": "%s", "owner": "%s",'
    self.CONF_STRING += '"dbusername": "%s","dbpass": "%s","dbname": "%s" } }'

  def fill_conf(self, event):
    linesplit = event.msg.split()
    try:
      server = linesplit[1] # .connect servername channelname port nick password
      channel = linesplit[2]
      port = linesplit[3]
    except IndexError:
      self.say(event.user, self.cmd)
      return None

    try:
      nick = linesplit[4]
    except IndexError:
      nick = self.bot.NICK

    try:
      password = linesplit[5]
    except IndexError:
      password = ""

    db_type = self.bot.conf.getDBType()
    db_name = self.bot.conf.getDBName(self.bot.network)
    db_username = self.bot.conf.getDBUsername(self.bot.network)
    db_pass = self.bot.conf.getDBPass(self.bot.network)
    owner = self.bot.conf.getOwner(self.bot.network)
    
    output = self.CONF_STRING % (db_type, server, channel, port, nick, password, 
                                      owner, db_username, db_pass, db_name)
    return output
    
  """
  we artificially generate a config and spawn another bot, then stick it in the botslist, then into the queue, so the original parent thread still has a handle on him
  """
  def handle(self, event):
    if not self.bot.brain._isAdmin(event.user):
      return
    import Queue
    q = Queue.Queue()
    a = self.fill_conf(event)
    f = self.bot.blist.get() # get the botslist out
    q.put(f)
    try:
      cm = ConfManager(a, string=True)
    except TypeError as e:
      e.args += (a,)
      self.bot.debug_print("error: ")
      self.bot.debug_print(e)
      self.bot.debug_print("a: ")
      self.bot.debug_print(a)
      return
    c = cm.getNetworks()
    b = Bot(conf=cm, network=c, d=self.bot.DEBUG, blist=q)
    b.start()
    self.bot.botslist.append(f)
