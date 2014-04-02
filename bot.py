#!/usr/bin/env python
#
# v0.6.5
# works with python 2.6.x and 2.7.x
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

import botbrain
from logger import Logger
import db
import confman
from event import Event
import db

DEBUG = False

class Bot(threading.Thread):
  def __init__(self, conf=None, network=None, d=None):
    threading.Thread.__init__(self)

    self.logger = Logger()

    self.logger.write(Logger.INFO, "\n")
    self.logger.write(Logger.INFO, " initializing bot, pid " + str(os.getpid()))

    self.DEBUG = d
    self.brain = None
    self.network = network
    self.OFFLINE = False
    self.CONNECTED = False
    self.JOINED = False
    self.conf = conf
    self.db = db.DB()
    self.pid = os.getpid()

    # arbitrary key/value store for modules
    # they should be 'namespaced' like bot.mem_store.module_name
    self.mem_store = dict()

    self.CHANNELINIT = conf.getChannels(self.network)
# this will be the socket
    self.s = None # each bot thread holds its own socket open to the network
    self.brain = botbrain.BotBrain(self.send, self) 

    self.events_list = list()

    # define events here and add them to the events_list

    joins = Event("__joins__")
    joins.define("JOIN")

    implying = Event("__implying__")
    implying.define(">")

    command = Event("__command__")
   # this is an example of passing in a regular expression to the event definition
    command.define("fo.bar")

    lastfm = Event("__.lastfm__")
    lastfm.define(".lastfm")

    dance = Event("__.dance__")
    dance.define("\.dance")

    pimp = Event("__pimp__")
    pimp.define("\.pimp")

    bofh = Event("__.bofh__")
    bofh.define("\.bofh")

    #youtube = Event("__youtubes__")
    #youtube.define("youtube.com[\S]+")

    weather = Event("__.weather__")
    weather.define("\.weather")

    steam = Event("__.steam__")
    steam.define("\.steam")

    part = Event("__.part__")
    part.define("part")

    tell = Event("__privmsg__")
    tell.define("PRIVMSG")

    unload = Event("__module__")
    unload.define("\.module")

    links = Event("__urls__")
    links.define("https?://*")

  # example
  #  test = Event("__test__")
  #  test.define(msg_definition="^\.test")

    # add your defined events here
    # tell your friends
    self.events_list.append(lastfm)
    self.events_list.append(dance)
    self.events_list.append(pimp)
    #self.events_list.append(youtube)
    self.events_list.append(bofh)
    self.events_list.append(weather)
    self.events_list.append(steam)
    self.events_list.append(part)
    self.events_list.append(tell)
    self.events_list.append(unload)
    self.events_list.append(links)
  # example
  #  self.events_list.append(test)

    self.load_modules()
    self.logger.write(Logger.INFO, "bot initialized.")

  # conditionally subscribe to events list or add event to listing
  def register_event(self, event, module):
    for e in self.events_list:
      if e.definition == event.definition and e._type == event._type:
        # if our event is already in the listing, don't add it again, just have our module subscribe
        e.subscribe(module)
        return

    self.events_list.append(event)
    return

  # utility function for loading modules; can be called by modules themselves
  def load_modules(self, specific=None):
    nonspecific = False
    found = False

    self.loaded_modules = list()

    modules_dir_list = list()
    tmp_list = list()
    
    modules_path = 'modules'
    autoload_path = 'modules/autoloads'

    # this is magic.

    import inspect
    import os, imp, json
    dir_list = os.listdir(modules_path)
    mods = {}
    autoloads = {}
    #load autoloads if it exists
    if os.path.isfile(autoload_path): 
      self.logger.write(Logger.INFO, "Found autoloads file")
      try:
        autoloads = json.load(open(autoload_path))
        #logging
        for k in autoloads.keys():
          self.logger.write(Logger.INFO, "Autoloads found for network " + k)
      except IOError:
        self.logger.write(Logger.ERROR, "Could not load autoloads file.")
    # create dictionary of things in the modules directory to load
    for fname in dir_list:
      name, ext = os.path.splitext(fname)
      if specific is None:
        nonspecific = True
        # ignore compiled python and __init__ files. 
        #choose to either load all .py files or, available, just ones specified in autoloads
        if self.network not in autoloads.keys(): # if autoload does not specify for this network
          if ext == '.py' and not name == '__init__': 
            f, filename, descr = imp.find_module(name, [modules_path])
            mods[name] = imp.load_module(name, f, filename, descr)
            self.logger.write(Logger.INFO, " loaded " + name + " for network " + self.network)
        else: # follow autoload's direction
          if ext == '.py' and not name == '__init__':
            if name == 'module':
              f, filename, descr = imp.find_module(name, [modules_path])
              mods[name] = imp.load_module(name, f, filename, descr)
              self.logger.write(Logger.INFO, " loaded " + name + " for network " + self.network)
            elif ('include' in autoloads[self.network] and name in autoloads[self.network]['include']) or ('exclude' in autoloads[self.network] and name not in autoloads[self.network]['exclude']):
              f, filename, descr = imp.find_module(name, [modules_path])
              mods[name] = imp.load_module(name, f, filename, descr)
              self.logger.write(Logger.INFO, " loaded " + name + " for network " + self.network)
      else:
        if name == specific: # we're reloading only one module
          if ext != '.pyc': # ignore compiled 
            f, filename, descr = imp.find_module(name, [modules_path])
            mods[name] = imp.load_module(name, f, filename, descr)
            found = True

    for k,v in mods.iteritems():
      for name in dir(v):
        obj = getattr(mods[k], name) # get the object from the namespace of 'mods'
        try:
          if inspect.isclass(obj): # it's a class definition, initialize it
            a = obj(self.events_list, self.send, self, self.say) # now we're passing in a reference to the calling bot
            if a not in self.loaded_modules: # don't add in multiple copies
              self.loaded_modules.append(a)
        except TypeError:
          pass

    if nonspecific is True or found is True:
      return 0
    else: return 1
    # end magic.
    
  def send(self, message):
    if self.OFFLINE:
      print str(datetime.datetime.now()) + ": " + self.getName() + ": " + message.encode('utf-8')
    else:
      if self.DEBUG is True:
        self.logger.write(Logger.INFO, "\n DEBUGGING OUTPUT")
        self.logger.write(Logger.INFO, str(datetime.datetime.now()) + ": " + self.getName() + ": " + message.encode('utf-8'))
        print str(datetime.datetime.now()) + ": " + self.getName() + ": " + message.encode('utf-8')

      self.s.send(message.encode('utf-8'))
      self.processline(':' + self.conf.getNick(self.network) + '!~' + self.conf.getNick(self.network) + '@fakehost.here ' + message.rstrip()) 

  def pong(self, response):
    self.send('PONG ' + response + '\n')

  def processline(self, line):
    if self.DEBUG:
      import datetime
      print str(datetime.datetime.now()) + ": " + self.getName() + ": " + line

    message_number = line.split()[1]

    try:
      for e in self.events_list:
        if e.matches(line):
          e.notifySubscribers(line)

  # don't bother going any further if it's a PING/PONG request
      if line.startswith("PING"):
        ping_response_line = line.split(":", 1)
        self.pong(ping_response_line[1])

      # pings we respond to directly. everything else...
      else:

# if we get disconnected this should be true upon a reconnect attempt.. ideally
        if self.JOINED is False and message_number == "376": # wait until we receive end of MOTD before joining
          self.chan_list = self.conf.getChannels(self.network) 
          for c in self.chan_list:
            self.send('JOIN '+c+' \n')
          self.JOINED = True
        
        line_array = line.split()
        user_and_mask = line_array[0][1:]
        usr = user_and_mask.split("!")[0]
        channel = line_array[2]
        try: 
          message = line.split(":",2)[2]
          self.brain.respond(usr, channel, message)
        except IndexError:
          try:
            message = line.split(":",2)[1]
            self.brain.respond(usr, channel, message)
          except IndexError:
            print "index out of range.", line
        
    except Exception:
      print "Unexpected error:", sys.exc_info()[0]
      traceback.print_exc(file=sys.stdout)

      
  def worker(self):
    self.HOST = self.network
    self.NICK = self.conf.getNick(self.network)

    # we have to cast it to an int, otherwise the connection fails silently and the entire process dies
    self.PORT = int(self.conf.getPort(self.network))
    self.IDENT = 'mypy'
    self.REALNAME = 's1ash'
    self.OWNER = self.conf.getOwner(self.network) 
    
    print os.getpid()
    # connect to server
    self.s = socket.socket()
    while self.CONNECTED == False:
      self.s.connect((self.HOST, self.PORT)) # force them into one argument
      self.CONNECTED = True

      self.s.send('NICK '+self.NICK+'\n')
      self.s.send('USER '+self.IDENT+ ' 8 ' + ' bla : '+self.REALNAME+'\n') # yeah, don't delete this line
      time.sleep(3) # allow services to catch up
      self.s.send('PRIVMSG nickserv identify '+self.conf.getIRCPass(self.network)+'\n')  # we're registered!

    self.s.setblocking(1)
    
    read = ""
    
    # infinite loop to keep parsing lines
    while True:
      try:
        time.sleep(1)
        if self.CONNECTED == False:
          self.connect()
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
      except KeyboardInterrupt:
        print "keyboard interrupt caught"
        raise
  # end worker

  def connect(self):
    time.sleep(10) # prevent attempting to reconnect too frequently errors
    self.s = socket.socket()
    try:
      self.s.connect((self.HOST, self.PORT)) # force them into one argument
    except Exception, e:
      self.CONNECTED = False
    try:
      self.s.send('NICK '+self.NICK+'\n')
      self.s.send('USER '+self.IDENT+ ' 8 ' + ' bla : '+self.REALNAME+'\n') # yeah, don't delete this line
      time.sleep(3) # allow services to catch up
      self.s.send('PRIVMSG nickserv identify '+self.conf.getIRCPass(self.network)+'\n')  # we're registered!
    except Exception, e:
      self.CONNECTED = False

    self.s.setblocking(1)
    
  def debug_print(self):
    print self.getName()

  def run(self):
    self.worker()

  def say(self, channel, thing):
    self.brain.say(channel, thing)
# end class Bot
              
## MAIN ## ACTUAL EXECUTION STARTS HERE

if __name__ == "__main__":
  import bot
  DEBUG = False
  for i in sys.argv:
    if i == "-d":
      DEBUG = True
  
  if os.name == "posix":
    botslist = list()
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
            b = bot.Bot(cm, net_list[i], DEBUG)
            b.start()
            i += 1
        else:
          b = bot.Bot(cm, net_list[0], DEBUG)
          b.start()
      elif pid > 0:
        print "forking to background..."
        sys.exit(0)
    else: # don't background
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
          try:
            b = bot.Bot(cm, net_list[i], DEBUG)
            b.daemon = True
            b.start()
            botslist.append(b)
            i += 1
            while True: time.sleep(5)
          except (KeyboardInterrupt, SystemExit):
            print "keyboard interrupt caught; exiting..."
            sys.exit(0)
      else:
        try:
          b = bot.Bot(cm, net_list[0], DEBUG)
          b.daemon = True
          b.start()
          botslist.append(b)
          while True: time.sleep(5)
        except (KeyboardInterrupt, SystemExit):
          print "keyboard interrupt caught; exiting..."
          sys.exit(0)
