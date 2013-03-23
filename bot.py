#!/usr/bin/env python
#
# v0.4
#
#


import sys
import socket
import string
import os
import datetime
import time
import select
import traceback
import threading

from multiprocessing import Process
import botbrain
import logger
import db
import confman
from event import Event
from util import import_all
from modules import *


class Bot(threading.Thread):
  def __init__(self, conf, network):
    threading.Thread.__init__(self)
    global DEBUG
    self.brain = None
    self.network = network
    DEBUG = True
    self.OFFLINE = False
#CHANNELINIT = ['#bots']
#CHANNELINIT = ['#bots', '#bf3', '#hhorg', '#dayz', '#cslug']
    self.CONNECTED = False
    self.conf = conf
    self.logger = logger.Logger()
    self.eventslist = list()

    self.CHANNELINIT = conf.getChannels(self.network)
    #self.network = conf.getNetwork()
# this will be the socket
    self.s = None # each bot thread holds its own socket open to the network
    self.brain = botbrain.BotBrain(self.send) # if this is unclear: send is a function pointer, to allow the botbrain to send

    
  def send(self, message):
    if self.OFFLINE:
      print message
    else:
      self.s.send(message)
      
    
  def pong(self, response):
    self.send('PONG ' + response + '\n')
    #date = str(time.strftime("%Y-%m-%d %H:%M:%S"))
    #l = logger.Logger()
    #l.write("responding to PING at " + date + '\n')
      

  def processline(self, line):
    if DEBUG:
      print self.getName() + ": " + line
      #self.logger.write(line+'\n')
    joins = Event("__joins__")
    joins.define("JOIN")

    modules = []
    library_list = []
    self.eventslist.append(joins)

    # library_list is a mapping of indices to imported, now anonymized, modules
    library_list = import_all("modules")
    for l in library_list:
      n = getattr(l, "__name__")
      print n

    from modules import n

    try:
      for e in self.eventslist:
        if e.matches(line):
          e.notifySubscribers(line)
      if line.startswith("PING"):
        ping_response_line = line.split(":", 1)
        self.pong(ping_response_line[1])

# current hackish solution for seen
# this is SO INCREDIBLY WRONG AND GROSS
      else:
# let's update the database because the events besides PRIVMSG never get past here
        if line.split()[1] == "JOIN" or line.split()[1] ==  "QUIT" or line.split()[1] == "PART":
      #   print line
          if "PART" in line:
            word = "PART"
# strip username out of line, lstrip for stripping out :
            self.brain._updateSeen(line.split("!",1)[0].lstrip(":"), line.rsplit(":",1)[-1], word)
          elif "JOIN" in line:
            word = "JOIN"
            self.brain._updateSeen(line.split("!",1)[0].lstrip(":"), "immmmmma joinin", word)
          else:
            word = "QUIT"
            self.brain._updateSeen(line.split("!",1)[0].lstrip(":"), line.rsplit(":",1)[-1], word)

        if self.CONNECTED is False:
          #self.logger.write("INSIDE SELF.CONNECTED\n")

          self.chan_list = self.conf.getChannels(self.network) 
          #if self.conf.getNumChannels(self.network) > 1:
          #  i = 0
          for c in self.chan_list:
            self.send('JOIN '+c+' \n')
          self.CONNECTED = True
          #else:
          #  self.send('JOIN '+self.chan_list+' \n')
          #  self.CONNECTED = True
        
        line_array = line.split()
        user_and_mask = line_array[0][1:]
        usr = user_and_mask.split("!")[0]
        channel = line_array[2]
        try: 
          message = line.split(":",2)[2]
          self.brain.respond(usr, channel, message)
        except IndexError:
          print "index out of range.", line
        
        #p = Process(target=botbrain.respond, args=(s, usr, channel, message))
        #p.start()
        
    except Exception:
      print "Unexpected error:", sys.exc_info()[0]
      traceback.print_exc(file=sys.stdout)
      
  def worker(self):
    try:
      if "minus22" in socket.gethostname() or "barge" in socket.gethostname():
        self.HOST = self.network
        self.NICK = 'ohai'
      else:
        self.HOST = self.network
        self.NICK = self.conf.getNick(self.network)
    except:
      self.HOST = self.network
      self.NICK = 'localohai'

    # we have to cast it to an int, otherwise the connection fails silently and the entire process dies
    #PORT = int(cm.getPort())
    self.PORT = int(self.conf.getPort(self.network))
    self.IDENT = 'mypy'
    self.REALNAME = 's1ash'
    self.OWNER = self.conf.getOwner(self.network) 
    
    print os.getpid()
    # connect to server
    self.s = socket.socket()
    try:
      self.s.connect((self.HOST, self.PORT)) # force them into one argument
    except Exception, e:
      print Exception, e
    try:
      self.s.send('NICK '+self.NICK+'\n')
      self.s.send('USER '+self.IDENT+ ' 8 ' + ' bla : '+self.REALNAME+'\n') # yeah, don't delete this line
      time.sleep(3) # allow services to catch up
      self.s.send('PRIVMSG nickserv identify '+self.conf.getIRCPass(self.network)+'\n')  # we're registered!
    except Exception, e:
      print Exception, e

    self.s.setblocking(1)
    
    read = ""
    
    # infinite loop to keep parsing lines
    while 1:
      time.sleep(1)
      ready = select.select([self.s],[],[], 1)
      if ready[0]:
        read = read + self.s.recv(1024)
        lines = read.split('\n')
        
        # Important: all lines from irc are terminated with '\n'. lines.pop() will get you any "to be continued"
        # line that couldn't fit in the socket buffer. It is stored and tacked on to the start of the next recv.
        read = lines.pop() 
        for line in lines:
          line = line.rstrip()
          self.processline(line)      

  def run(self):
    self.worker()
# end class Bot
              
## MAIN ## ACTUAL EXECUTION STARTS HERE

if __name__ == "__main__":
  import bot
  #if DEBUG:
  # worker() # run in foreground for debugging
  #
  #else:
  DEBUG = False
  for i in sys.argv:
    if i == "-d":
      DEBUG = True
  
  if os.name == "posix":
    if not DEBUG:
      pid = os.fork()
      if pid == 0: # child
        if len(sys.argv) > 1:
          CONF = sys.argv[1]
        else: CONF = "~/.pybotrc"

        cm = confman.ConfManager(CONF)
        net_list = cm.getNetworks()
        i = 0
        if cm.getNumNets() > 1:
          for c in cm.getNetworks():
            b = bot.Bot(cm, net_list[i])
            b.start()
            i += 1
        else:
          b = bot.Bot(cm, net_list[0])
          b.start()
      elif pid > 0:
        print "forking to background..."
        sys.exit(0)
    else: # don't background
      import bot
      if len(sys.argv) > 1 and sys.argv[1] != "-d": # the conf file must be first argument
        CONF = sys.argv[1]
        try:
          f = open(CONF)
        except IOError:
          print "Could not open conf file " + sys.argv[1]
          sys.exit(1)
      else: CONF = "~/.pybotrc"

      cm = confman.ConfManager(CONF)
      net_list = cm.getNetworks()
      i = 0
      if cm.getNumNets() > 1:
        for c in cm.getNetworks():
          b = bot.Bot(cm, net_list[i])
          b.start()
          i += 1
      else:
        b = bot.Bot(cm, net_list[0])
        b.start()
      

# else: # since we don't have fork on windows
#   p = Process(target=worker)
#   p.start()
#   print os.getpid()
