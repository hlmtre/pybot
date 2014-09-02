#!/usr/bin/env python
#
# v0.7.0
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
import util

DEBUG = False

class Bot(threading.Thread):
  def __init__(self, conf=None, network=None, d=None):
    threading.Thread.__init__(self)

    self.DEBUG = d
    self.brain = None
    self.network = network
    self.OFFLINE = False
    self.CONNECTED = False
    self.JOINED = False
    self.conf = conf
    self.db = db.DB()
    self.pid = os.getpid()
    self.logger = Logger()

    self.NICK = self.conf.getNick(self.network)

    self.logger.write(Logger.INFO, "\n", self.NICK)
    self.logger.write(Logger.INFO, " initializing bot, pid " + str(os.getpid()), self.NICK)

    # arbitrary key/value store for modules
    # they should be 'namespaced' like bot.mem_store.module_name
    self.mem_store = dict()

    self.CHANNELINIT = conf.getChannels(self.network)
# this will be the socket
    self.s = None # each bot thread holds its own socket open to the network
    self.brain = botbrain.BotBrain(self.send, self) 

    self.events_list = list()

    # define events here and add them to the events_list

    all_lines = Event("1__all_lines__")
    all_lines.define(".*")
    self.events_list.append(all_lines)

    implying = Event("__implying__")
    implying.define(">")

    #command = Event("__command__")
   # this is an example of passing in a regular expression to the event definition
    #command.define("fo.bar")

    lastfm = Event("__.lastfm__")
    lastfm.define(".lastfm")

    dance = Event("__.dance__")
    dance.define("\.dance")

    #unloads = Event("__module__")
    #unloads.define("^\.module")

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
    self.events_list.append(links)
    #self.events_list.append(unloads)
  # example
  #  self.events_list.append(test)

    self.load_modules()
    self.logger.write(Logger.INFO, "bot initialized.", self.NICK)

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
      self.logger.write(Logger.INFO, "Found autoloads file", self.NICK)
      try:
        autoloads = json.load(open(autoload_path))
        #logging
        for k in autoloads.keys():
          self.logger.write(Logger.INFO, "Autoloads found for network " + k, self.NICK)
      except IOError:
        self.logger.write(Logger.ERROR, "Could not load autoloads file.",self.NICK)
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
            self.logger.write(Logger.INFO, " loaded " + name + " for network " + self.network, self.NICK)
        else: # follow autoload's direction
          if ext == '.py' and not name == '__init__':
            if name == 'module':
              f, filename, descr = imp.find_module(name, [modules_path])
              mods[name] = imp.load_module(name, f, filename, descr)
              self.logger.write(Logger.INFO, " loaded " + name + " for network " + self.network, self.NICK)
            elif ('include' in autoloads[self.network] and name in autoloads[self.network]['include']) or ('exclude' in autoloads[self.network] and name not in autoloads[self.network]['exclude']):
              f, filename, descr = imp.find_module(name, [modules_path])
              mods[name] = imp.load_module(name, f, filename, descr)
              self.logger.write(Logger.INFO, " loaded " + name + " for network " + self.network, self.NICK)
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
      self.debug_print(util.bcolors.YELLOW + " >> " + util.bcolors.ENDC + self.getName() + ": " + message.encode('utf-8', 'ignore'))
    else:
      if self.DEBUG is True:
        self.logger.write(Logger.INFO, "\n DEBUGGING OUTPUT", self.NICK)
        self.logger.write(Logger.INFO, str(datetime.datetime.now()) + ": " + self.getName() + ": " + message.encode('utf-8', 'ignore'), self.NICK)
        self.debug_print(util.bcolors.OKGREEN + ">> " + util.bcolors.ENDC + ": " + self.getName() + ": " + message.encode('utf-8', 'ignore'))

      self.s.send(message.encode('utf-8', 'ignore'))
      target = message.split()[1]
      if target.startswith("#"):
        self.processline(':' + self.conf.getNick(self.network) + '!~' + self.conf.getNick(self.network) + '@fakehost.here ' + message.rstrip()) 

  def pong(self, response):
    self.send('PONG ' + response + '\n')

  def processline(self, line):
    if self.DEBUG:
      import datetime
      self.debug_print(util.bcolors.OKBLUE + "<< "  + util.bcolors.ENDC + ": " + self.getName() + ": " + line)

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
# patch contributed by github.com/thekanbo
        if self.JOINED is False and (message_number == "376" or message_number == "422"): 
          # wait until we receive end of MOTD before joining, or until the server tells us the MOTD doesn't exis
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

      
  def worker(self, mock=False):
    self.HOST = self.network
    self.NICK = self.conf.getNick(self.network)

    # we have to cast it to an int, otherwise the connection fails silently and the entire process dies
    self.PORT = int(self.conf.getPort(self.network))
    self.IDENT = 'mypy'
    self.REALNAME = 's1ash'
    self.OWNER = self.conf.getOwner(self.network) 
    
    # connect to server
    self.s = socket.socket()
    while self.CONNECTED == False:
      try:
# low level socket TCP/IP connection
        self.s.connect((self.HOST, self.PORT)) # force them into one argument
        self.CONNECTED = True
        self.logger.write(Logger.INFO, "Connected to " + self.network, self.NICK)
        if self.DEBUG:
          self.debug_print(util.bcolors.YELLOW + ">> " + util.bcolors.ENDC + "connected to " + self.network)
      except:
        self.debug_print(util.bcolors.FAIL + ">> " + util.bcolors.ENDC + "Could not connect! Retrying... ")
        time.sleep(1)
        self.worker()

    # core IRC protocol stuff
      self.s.send('NICK '+self.NICK+'\n')

      if self.DEBUG:
        self.debug_print(util.bcolors.YELLOW + ">> " + util.bcolors.ENDC + self.network + ': NICK ' + self.NICK + '\\n')

      self.s.send('USER '+self.IDENT+ ' 8 ' + ' bla : '+self.REALNAME+'\n') # yeah, don't delete this line

      if self.DEBUG:
        self.debug_print(util.bcolors.YELLOW + ">> " + util.bcolors.ENDC + self.network + ": USER " +self.IDENT+ ' 8 ' + ' bla : '+self.REALNAME+'\\n')

      time.sleep(3) # allow services to catch up

      self.s.send('PRIVMSG nickserv identify '+self.conf.getIRCPass(self.network)+'\n')  # we're registered!

      if self.DEBUG:
        self.debug_print(util.bcolors.YELLOW + ">> " + util.bcolors.ENDC + self.network + ': PRIVMSG nickserv identify '+self.conf.getIRCPass(self.network)+'\\n')

    self.s.setblocking(1)
    
    read = ""
    
    timeout = 0

#   if we're only running a test of connecting, and don't want to loop forever
    if mock:
      return
    # infinite loop to keep parsing lines
    while True:
      try:
        timeout += 1
        # if we haven't received anything for 120 seconds
        time_since = self.conf.getTimeout(self.network)
        if timeout > time_since:
          if self.DEBUG:
            print "Disconnected! Retrying... "
          self.logger.write(Logger.CRITICAL, "Disconnected!", self.NICK)
# so that we rejoin all our channels upon reconnecting to the server
          self.JOINED = False
          self.CONNECTED = False
          self.worker()

        time.sleep(1)
       # if self.CONNECTED == False:
       #   self.connect()
        ready = select.select([self.s],[],[], 1)
        if ready[0]:
          try:
            read = read + self.s.recv(1024)
          except:
            if self.DEBUG:
              print "Disconnected! Retrying... "
            self.logger.write(Logger.CRITICAL, "Disconnected!", self.NICK)
            self.JOINED = False
            self.CONNECTED = False
            self.worker()

          lines = read.split('\n')
          
          # Important: all lines from irc are terminated with '\n'. lines.pop() will get you any "to be continued"
          # line that couldn't fit in the socket buffer. It is stored and tacked on to the start of the next recv.
          read = lines.pop() 

          if len(lines) > 0:
            timeout = 0

          for line in lines:
            line = line.rstrip()
            self.processline(line)      
      except KeyboardInterrupt:
        print "keyboard interrupt caught; exiting ..."
        raise
  # end worker

  def debug_print(self, line):
    print str(datetime.datetime.now()) + ": " + self.getName() + ": " + line

  def commands(*command_list):
# stolen shamelessly from willie. damn, this is a good idea.
    """Decorator. Sets a command list for a callable.

    This decorator can be used to add multiple commands to one callable in a
    single line. The resulting match object will have the command as the first
    group, rest of the line, excluding leading whitespace, as the second group.
    Parameters 1 through 4, seperated by whitespace, will be groups 3-6.

    Args:
    command: A string, which can be a regular expression.

    Returns:
    A function with a new command appended to the commands
    attribute. If there is no commands attribute, it is added.

    Example:
    @command("hello"):
    If the command prefix is "\.", this would trigger on lines starting
    with ".hello".

    @commands('j', 'join')
    If the command prefix is "\.", this would trigger on lines starting
    with either ".j" or ".join".

    """
    def add_attribute(function):
      if not hasattr(function, "commands"):
        function.commands = []
      function.commands.extend(command_list)
      return function
    return add_attribute

  def depends(self, module_name):
    for m in self.loaded_modules:
      if m.__class__.__name__ == module_name:
        return m
    return None
    
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

# duuude this is so old.
  if os.name == "posix":
    botslist = list()
    if not DEBUG:
      pid = os.fork()
      if pid == 0: # child
        print "starting bot in the background, pid " + util.bcolors.GREEN + str(os.getpid()) + util.bcolors.ENDC
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
        sys.exit(0)
    else: # don't background
      print "starting bot in the background, pid " + util.bcolors.GREEN + str(os.getpid()) + util.bcolors.ENDC
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
