#!/usr/bin/env python2
#
# see version.py for version
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
import inspect
import argparse

import botbrain
from logger import Logger
import confman
from event import Event
import util

DEBUG = False
RETRY_COUNTER = 0

class Bot(threading.Thread):
  """
    bot instance. one bot gets instantiated per network, as an entirely distinct, sandboxed thread.
    handles the core IRC protocol stuff, and passing lines to defined events, which dispatch to their subscribed modules.
  """
  def __init__(self, conf=None, network=None, d=None):
    threading.Thread.__init__(self)

    self.HOST = None
    self.PORT = None
    self.REALNAME = None
    self.IDENT = None
    self.DEBUG = d
    self.brain = None
    self.network = network
    self.OFFLINE = False
    self.CONNECTED = False
    self.JOINED = False
    self.conf = conf
    self.pid = os.getpid()
    self.logger = Logger()
#   to be a dict of dicts
    self.command_function_map = dict()
    
    if self.conf.getDBType() == "sqlite":
      import lite
      self.db = lite.SqliteDB(self)
    else: 
      import db
      self.db = db.DB(self)


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
    """
      Allows for dynamic, asynchronous event creation. To be used by modules, mostly, to define their own events in their initialization.
      Prevents multiple of the same _type of event being registered.

      Args: 
      event: an event object to be registered with the bot 
      module: calling module; ensures the calling module can be subscribed to the event if it is not already.

      Returns: 
      nothing.
    """
    for e in self.events_list:
      if e.definition == event.definition and e._type == event._type:
        # if our event is already in the listing, don't add it again, just have our module subscribe
        e.subscribe(module)
        return

    self.events_list.append(event)
    return

  def load_snippets(self):
    import imp
    snippets_path = self.modules_path + '/snippets'
    self.snippets_list = set()
# load up snippets first
    for filename in os.listdir(snippets_path):
      name, ext = os.path.splitext(filename)
      try:
        if ext == ".py":
# snippet is a module
          snippet = imp.load_source(name, snippets_path + '/' + filename)
          self.snippets_list.add(snippet)
      except Exception, e:
        print e
        print name, filename

  def set_snippets(self):
    """ 
    check each snippet for a function with a list of commands in it
    create a big ol list of dictionaries, commands mapping to the functions to call if the command is encountered
    """
    for obj in self.snippets_list:
      for k,v in inspect.getmembers(obj, inspect.isfunction):
        if inspect.isfunction(v) and hasattr(v, 'commands'):
          for c in v.commands:
            if not c in self.command_function_map:
              self.command_function_map[c] = dict()
            self.command_function_map[c] = v


  # utility function for loading modules; can be called by modules themselves
  def load_modules(self, specific=None):
    """
      Run through the ${bot_dir}/modules directory, dynamically instantiating each module as it goes.

      Args:
      specific: string name of module. if it is specified, the function attempts to load the named module.

      Returns:
      1 if successful, 0 on failure. In keeping with the perverse reversal of UNIX programs and boolean values.
    """
    nonspecific = False
    found = False

    self.loaded_modules = list()

    modules_dir_list = list()
    tmp_list = list()
    
    self.modules_path = 'modules'
    modules_path = 'modules'
    self.autoload_path = 'modules/autoloads'
    autoload_path = 'modules/autoloads'

    # this is magic.

    import os, imp, json


    self.load_snippets()
    self.set_snippets()

    dir_list = os.listdir(modules_path)
    mods = {}
    autoloads = {}
    # load autoloads if it exists
    if os.path.isfile(autoload_path): 
      self.logger.write(Logger.INFO, "Found autoloads file", self.NICK)
      try:
        autoloads = json.load(open(autoload_path))
        # logging
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
        # choose to either load all .py files or, available, just ones specified in autoloads
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
    else:
      return 1
    # end magic.
    
  def send(self, message):
    """
    Simply sends the specified message to the socket. Which should be our connected server.
    We parse our own lines, as well, in case we want an event triggered by something we say.
    If debug is True, we also print out a pretty thing to console.

    Args:
    message: string, sent directly and without manipulation (besides UTF-8ing it) to the server.
    """
    if self.OFFLINE:
      self.debug_print(util.bcolors.YELLOW + " >> " + util.bcolors.ENDC + self.getName() + ": " + message.encode('utf-8', 'ignore'))
    else:
      if self.DEBUG is True:
        self.logger.write(Logger.INFO, "DEBUGGING OUTPUT", self.NICK)
        self.logger.write(Logger.INFO, self.getName() + " " + message.encode('utf-8', 'ignore'), self.NICK)
        self.debug_print(util.bcolors.OKGREEN + ">> " + util.bcolors.ENDC + ": " + " " + message.encode('utf-8', 'ignore'))

      self.s.send(message.encode('utf-8', 'ignore'))
      target = message.split()[1]
      if target.startswith("#"):
        self.processline(':' + self.conf.getNick(self.network) + '!~' + self.conf.getNick(self.network) + '@fakehost.here ' + message.rstrip()) 

  def pong(self, response):
    """
    Keepalive heartbeat for IRC protocol. Until someone changes the IRC spec, don't modify this.
    """
    self.send('PONG ' + response + '\n')

  def processline(self, line):
    """
    Grab newline-delineated lines sent to us, and determine what to do with them. 
    This function handles our initial low-level IRC stuff, as well; if we haven't joined, it waits for the MOTD message (or message indicating there isn't one) and then issues our own JOIN calls.

    Also immediately passes off PING messages to PONG.

    Args:
    line: string. 

    """
    if self.DEBUG:
      import datetime
      if os.name == "posix": # because windows doesn't like the color codes.
        self.debug_print(util.bcolors.OKBLUE + "<< " + util.bcolors.ENDC + line)
      else:
        self.debug_print("<< " + ": " + line)

    message_number = line.split()[1]

    try:
      first_word = line.split(":", 2)[2].split()[0]
      channel = line.split()[2]
    except IndexError:
      pass
    else:
      if first_word in self.command_function_map:
        self.command_function_map[first_word](self, line, channel)

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
          # wait until we receive end of MOTD before joining, or until the server tells us the MOTD doesn't exist
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
    """
    Open the socket, make the first incision^H^H connection and get us on the server. 
    Handles keeping the connection alive; if we disconnect from the server, attempts to reconnect.

    Args:
    mock: boolean. If mock is true, don't loop forever -- mock is for testing.
    """
    self.HOST = self.network
    self.NICK = self.conf.getNick(self.network)

    # we have to cast it to an int, otherwise the connection fails silently and the entire process dies
    self.PORT = int(self.conf.getPort(self.network))
    self.IDENT = 'mypy'
    self.REALNAME = 's1ash'
    self.OWNER = self.conf.getOwner(self.network) 
    
    # connect to server
    self.s = socket.socket()
    while not self.CONNECTED:
      try:
# low level socket TCP/IP connection
        self.s.connect((self.HOST, self.PORT)) # force them into one argument
        self.CONNECTED = True
        self.logger.write(Logger.INFO, "Connected to " + self.network, self.NICK)
        if self.DEBUG:
          self.debug_print(util.bcolors.YELLOW + ">> " + util.bcolors.ENDC + "connected to " + self.network)
      except:
        if self.DEBUG:
          self.debug_print(util.bcolors.FAIL + ">> " + util.bcolors.ENDC + "Could not connect to " + self.HOST + " at " + str(self.PORT) + "! Retrying... ")
        self.logger.write(Logger.CRITICAL, "Could not connect to " + self.HOST + " at " + str(self.PORT) + "! Retrying...")
        time.sleep(1)

        self.worker()

      time.sleep(1)
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

#   does not require a definition -- it will be invoked specifically when the bot notices it has been disconnected
    disconnect_event = Event("__.disconnection__")
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
            self.debug_print("Disconnected! Retrying... ")
          disconnect_event.notifySubscribers("null")
          self.logger.write(Logger.CRITICAL, "Disconnected!", self.NICK)
# so that we rejoin all our channels upon reconnecting to the server
          self.JOINED = False
          self.CONNECTED = False

          global RETRY_COUNTER
          if RETRY_COUNTER > 10:
            self.debug_print("Failed to reconnect after 10 tries. Giving up...")
            sys.exit(1)

          RETRY_COUNTER+=1
          self.worker()

        time.sleep(1)
        ready = select.select([self.s], [], [], 1)
        if ready[0]:
          try:
            read = read + self.s.recv(1024).decode('utf8', 'ignore')
          except UnicodeDecodeError, e:
            self.debug_print("Unicode decode error; " + e.__str__())
            self.debug_print("Offending recv: " + self.s.recv)
            pass
          except Exception, e:
            print e
            if self.DEBUG:
              self.debug_print("Disconnected! Retrying... ")
            disconnect_event.notifySubscribers("null")
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

  def debug_print(self, line, error=False):
    """
    Prepends incoming lines with the current timestamp and the thread's name, then spits it to stdout.
    Warning: this is entirely asynchronous between threads. If you connect to multiple networks, they will interrupt each other between lines.

    Args:
    line: text.
    error: boolean, defaults to False. if True, prints out with red >> in the debug line
    """

    if not error:
      print str(datetime.datetime.now()) + ": " + self.getName() + ": " + line.strip('\n').rstrip().lstrip()
    else:
      print str(datetime.datetime.now()) + ": " + self.getName() + ": " + util.bcolors.RED + ">> " + util.bcolors.ENDC + line.strip('\n').rstrip().lstrip()

    
  def run(self):
    """
    For implementing the parent threading.Thread class. Allows the thread the be initialized with our code.
    """
    self.worker()

  def say(self, channel, thing):
    """
    Speak, damn you!
    """
    self.brain.say(channel, thing)
# end class Bot
              
## MAIN ## ACTUAL EXECUTION STARTS HERE

if __name__ == "__main__":
  DEBUG = False
  import bot

  parser = argparse.ArgumentParser(description="a python irc bot that does stuff")
  parser.add_argument('config', nargs='?')
  parser.add_argument('-d', help='debug (foreground) mode', action='store_true')

  args = parser.parse_args()
  if args.d:
    DEBUG = True
  if args.config:
    config = args.config
  else:
    config = "~/.pybotrc"

  botslist = list()
  if not DEBUG and hasattr(os, 'fork'):
    pid = os.fork()
    if pid == 0: # child
      if os.name == "posix":
        print "starting bot in the background, pid " + util.bcolors.GREEN + str(os.getpid()) + util.bcolors.ENDC
      else:
        print "starting bot in the background, pid " + str(os.getpid())

      cm = confman.ConfManager(config)
      net_list = cm.getNetworks()
      for c in cm.getNetworks():
        b = bot.Bot(cm, c, DEBUG)
        b.start()

    elif pid > 0:
      sys.exit(0)
  else: # don't background; either we're in debug (foreground) mode, or on windows TODO
    if os.name == 'nt':
      print 'in debug mode; backgrounding currently unsupported on windows.'
    DEBUG = True
    print "starting bot, pid " + util.bcolors.GREEN + str(os.getpid()) + util.bcolors.ENDC
    try:
      f = open(os.path.expanduser(config))
    except IOError:
      print "Could not open conf file " + config 
      sys.exit(1)

    cm = confman.ConfManager(config)
    net_list = cm.getNetworks()
    for c in cm.getNetworks():
      b = bot.Bot(cm, c, DEBUG)
      b.daemon = True
      b.start()
      botslist.append(b)
    try:
      while True:
        time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
      l = Logger()
      l.write(Logger.INFO, "killed by ctrl+c or term signal")
      for b in botslist:
        b.s.send("QUIT :because I got killed\n")
      print
      print "keyboard interrupt caught; exiting"
      sys.exit(1)
      

