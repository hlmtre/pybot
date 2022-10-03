#
# see version.py for version
# works with python 2.7.x and 3 (!!)
#


import datetime
import inspect
import os
import pickle
import select
import socket
import sys
import threading
import time
import traceback
from collections import deque

from util import parse_line
import scheduler
import botbrain
import util
from event import Event
from logger import Logger

DEBUG = False
RETRY_COUNTER = 0


class Bot(threading.Thread):
    """
      bot instance. one bot gets instantiated per network, as an entirely distinct, sandboxed thread.
      handles the core IRC protocol stuff, and passing lines to defined events, which dispatch to their subscribed modules.
    """

    def __init__(self, conf=None, network=None, d=None, local_nickname=None,
                 local_channels=None, local_port=None, local_owner=None):
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
        self.OWNER = local_owner
        self.chan_list = None
        self.pid = os.getpid()
        self.logger = Logger()
#   to be a dict of dicts
        self.command_function_map = dict()
        self.snippets_list = set()
        self.recent_lines = deque(maxlen=15)

        self.scheduler = scheduler.Scheduler(self)
        self.scheduler.daemon = True
        self.scheduler.start()

        if conf is None:
            class Mockuconf:
                def __init__(self, bot=None):
                    self.network = network

                def getDBType(self, net=None):
                    return "sqlite"

                def getNick(self, net=None):
                    return local_nickname

                def getOwner(self, net=None):
                    if local_owner is not None:
                        return local_owner
                    else:
                        return "hlmtre"

                def getPort(self, net=None):
                    if local_port is not None:
                        return local_port
                    else:
                        return 6667
            conf = Mockuconf()

        self.conf = conf

        try:
            if self.conf.getDBType() == "sqlite":
                import lite
                self.db = lite.SqliteDB(self)
            else:
                import db
                self.db = db.DB(self)
        except AttributeError:
            import lite
            self.db = lite.SqliteDB(self)

        if not local_nickname:
            self.NICK = self.conf.getNick(self.network)
        else:
            self.NICK = local_nickname

        self.logger.write(Logger.INFO, "\n", self.NICK)
        self.logger.write(Logger.INFO,
                          " initializing bot, pid " + str(os.getpid()),
                          self.NICK)

        # arbitrary key/value store for modules
        # they should be 'namespaced' like bot.mem_store.module_name
        self.mem_store = dict()
        self.persistence = list()
        # after the mem_store is instantiated, reload pickled objects
        self.load_persistence()

        if local_channels is not None:
            self.chan_list = local_channels.split(",")
# this will be the socket
        self.s = None  # each bot thread holds its own socket open to the network

        self.brain = botbrain.BotBrain(self.send, self)

        self.events_list = list()

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
        if self.events_list is not None:
            for e in self.events_list:
                if e.definition == event.definition and e._type == event._type:
                    # if our event is already in the listing, don't add it
                    # again, just have our module subscribe
                    e.subscribe(module)
                    return

        self.events_list.append(event)
        return

    def has_event(self, event):
        if self.events_list is not None:
            for e in self.events_list:
                if e.definition == event.definition and e._type == event._type:
                    # if our event is already in the listing, don't add it
                    # again, just have our module subscribe
                    return True
        return False

    def load_snippets(self):
        import imp
        snippets_path = self.modules_path + '/snippets'
# load up snippets first
        for filename in os.listdir(snippets_path):
            name, ext = os.path.splitext(filename)
            try:
                if ext == ".py":
                    # snippet is a module
                    snippet = imp.load_source(
                        name, snippets_path + '/' + filename)
                    self.snippets_list.add(snippet)
            except Exception as e:
                print(e)
                print((name, filename))

    def persist(self, namespace):
        self.persistence.append(namespace)

    def save_persistence(self):
        print(self.persistence)
        if not os.path.exists('pickle/'):
            os.makedirs('pickle')
        for n in self.persistence:
            pickle.dump(self.mem_store[n], 'pickle/' + n, 'wb')

    def load_persistence(self):
        if not os.path.exists('pickle/'):
            os.makedirs('pickle')
        for f in os.listdir('pickle'):
            # don't unpickle current directory (.) or up one (..) because those
            # aren't pickled objects
            if f == "." or f == "..":
                continue
            self.mem_store[f] = pickle.load(open('pickle/' + f, 'rb'))
            # XXX YOU'RE GOING TO SAVE QDACS WITH PERSIST

    def set_snippets(self):
        """
        check each snippet for a function with a list of commands in it
        create a big ol list of dictionaries, commands mapping to the functions to call if the command is encountered
        """
        for obj in self.snippets_list:
            for k, v in inspect.getmembers(obj, inspect.isfunction):
                if inspect.isfunction(v) and hasattr(v, 'commands'):
                    for c in v.commands:
                        if c not in self.command_function_map:
                            self.command_function_map[c] = dict()
                        self.command_function_map[c] = v

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

        self.modules_path = 'modules'
        self.autoload_path = 'modules/autoloads'

        # this is magic.

        import imp
        import json

        self.load_snippets()
        self.set_snippets()

        dir_list = os.listdir(self.modules_path)
        mods = {}
        autoloads = {}
        # load autoloads if it exists
        if os.path.isfile(self.autoload_path):
            self.logger.write(Logger.INFO, "Found autoloads file", self.NICK)
            try:
                autoloads = json.load(open(self.autoload_path))
                # logging
                for k in list(autoloads.keys()):
                    self.logger.write(
                        Logger.INFO, "Autoloads found for network " + k, self.NICK)
                    if self.DEBUG:
                        self.debug_print(
                            util.bcolors.OKGREEN +
                            ">>" +
                            util.bcolors.ENDC +
                            " Autoloads found for network " +
                            k)
            except IOError:
                self.logger.write(
                    Logger.WARNING,
                    "Could not load autoloads file.",
                    self.NICK)
                if self.DEBUG:
                    self.debug_print(
                        util.bcolors.WARNING +
                        ">>" +
                        util.bcolors.ENDC +
                        " Could not load autoloads file " +
                        k)
        # create dictionary of things in the modules directory to load
        for fname in dir_list:
            name, ext = os.path.splitext(fname)
            if specific is None:
                nonspecific = True
                # ignore compiled python and __init__ files.
                # choose to either load all .py files or, available, just ones
                # specified in autoloads
                if self.network not in list(
                        autoloads.keys()):  # if autoload does not specify for this network
                    if ext == '.py' and not name == '__init__':
                        f, filename, descr = imp.find_module(
                            name, [self.modules_path])
                        mods[name] = imp.load_module(name, f, filename, descr)
                        self.logger.write(
                            Logger.INFO,
                            " loaded " +
                            name +
                            " for network " +
                            self.network,
                            self.NICK)
                        if self.DEBUG:
                            self.debug_print(
                                util.bcolors.OKGREEN +
                                ">>" +
                                util.bcolors.ENDC +
                                " Loaded " +
                                name +
                                " for network " +
                                self.network)
                else:  # follow autoload's direction
                    if ext == '.py' and not name == '__init__':
                        if name == 'module':
                            f, filename, descr = imp.find_module(
                                name, [self.modules_path])
                            mods[name] = imp.load_module(
                                name, f, filename, descr)
                            self.logger.write(
                                Logger.INFO,
                                " loaded " +
                                name +
                                " for network " +
                                self.network,
                                self.NICK)
                            if self.DEBUG:
                                self.debug_print(
                                    util.bcolors.OKGREEN +
                                    ">>" +
                                    util.bcolors.ENDC +
                                    " Loaded " +
                                    name +
                                    " for network " +
                                    self.network)
                        elif (
                                ('include' in autoloads[self.network]
                                 and name in autoloads[self.network]['include'])
                                or ('exclude' in autoloads[self.network]
                                    and name not in autoloads[self.network]['exclude'])
                                ):
                            f, filename, descr = imp.find_module(
                                name, [self.modules_path])
                            mods[name] = imp.load_module(
                                name, f, filename, descr)
                            self.logger.write(
                                Logger.INFO,
                                " loaded " +
                                name +
                                " for network " +
                                self.network,
                                self.NICK)
                            if self.DEBUG:
                                self.debug_print(
                                    util.bcolors.OKGREEN +
                                    ">>" +
                                    util.bcolors.ENDC +
                                    " Loaded " +
                                    name +
                                    " for network " +
                                    self.network)
            else:
                if name == specific:  # we're reloading only one module
                    if ext != '.pyc':  # ignore compiled
                        f, filename, descr = imp.find_module(
                            name, [self.modules_path])
                        mods[name] = imp.load_module(name, f, filename, descr)
                        found = True

        for k, v in list(mods.items()):
            for name in dir(v):
                # get the object from the namespace of 'mods'
                obj = getattr(mods[k], name)
                try:
                    if inspect.isclass(
                            obj):  # it's a class definition, initialize it
                        # now we're passing in a reference to the calling bot
                        a = obj(self.events_list, self.send, self, self.say)
                        if a not in self.loaded_modules:  # don't add in multiple copies
                            self.loaded_modules.append(a)
                except TypeError:
                    pass

        if nonspecific is True or found is True:
            return 0
        return 1
        # end magic.
        # this really is fucking magic.

    def send(self, message):
        """
        Simply sends the specified message to the socket. Which should be our connected server.
        We parse our own lines, as well, in case we want an event triggered by something we say.
        If debug is True, we also print out a pretty thing to console.

        Args:
        message: string, sent directly and without manipulation (besides UTF-8ing it) to the server.
        """
        if self.OFFLINE:
            self.debug_print(
                util.bcolors.YELLOW +
                " >> " +
                util.bcolors.ENDC +
                self.getName() +
                ": " +
                message.encode(
                    'utf-8',
                    'ignore'))
        else:
            if self.DEBUG is True:
                self.logger.write(Logger.INFO, "DEBUGGING OUTPUT", self.NICK)
                if isinstance(message, bytes):
                    self.logger.write(
                        Logger.INFO,
                        self.getName() +
                        " " +
                        message.decode(
                            'utf-8',
                            'ignore'),
                        self.NICK)
                else:
                    self.logger.write(
                        Logger.INFO, self.getName() + " " + message, self.NICK)
                if isinstance(message, bytes):
                    self.debug_print(
                        util.bcolors.OKGREEN +
                        ">> " +
                        util.bcolors.ENDC +
                        ": " +
                        " " +
                        message.decode(
                            'utf-8',
                            'ignore'))
                else:
                    self.debug_print(
                        util.bcolors.OKGREEN +
                        ">> " +
                        util.bcolors.ENDC +
                        ": " +
                        " " +
                        message)

            if not isinstance(message, bytes):
                self.s.send(message.encode('utf-8', 'ignore'))
            else:
                self.s.send(message)
            target = message.split()[1]
            if isinstance(target, bytes):
                target = target.decode()
            if target.startswith('#'):
                if isinstance(message, bytes):
                    self.processline(
                        ':' +
                        self.conf.getNick(
                            self.network) +
                        '!~' +
                        self.conf.getNick(
                            self.network) +
                        '@fakehost.here ' +
                        message.decode().rstrip())
                elif isinstance(message, str):
                    self.processline(
                        ':' +
                        self.conf.getNick(
                            self.network) +
                        '!~' +
                        self.conf.getNick(
                            self.network) +
                        '@fakehost.here ' +
                        message.rstrip())

    def pong(self, response):
        """
        Keepalive heartbeat for IRC protocol. Until someone changes the IRC spec, don't modify this.
        """
        self.send(('PONG ' + response + '\n').encode())

    def bare_send(self, line):
        self.send((line + '\n').encode())

    def processline(self, line):
        """
        Grab newline-delineated lines sent to us, and determine what to do with them.
        This function handles our initial low-level IRC stuff, as well; if we haven't joined, it waits for the MOTD message (or message indicating there isn't one) and then issues our own JOIN calls.

        Also immediately passes off PING messages to PONG.

        Args:
        line: string.

        """

        self.recent_lines.appendleft(line)
        if self.DEBUG:
            if os.name == "posix":  # because windows doesn't like the color codes.
                self.debug_print(
                    util.bcolors.OKBLUE +
                    "<< " +
                    util.bcolors.ENDC +
                    line)
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
                self.command_function_map[first_word](self, parse_line(line).message, channel)

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
                if self.JOINED is False and (
                        message_number == "376" or message_number == "422"):
                    # wait until we receive end of MOTD before joining, or
                    # until the server tells us the MOTD doesn't exist
                    if not self.chan_list:
                        self.chan_list = self.conf.getChannels(self.network)
                    for c in self.chan_list:
                        self.send(('JOIN ' + c + ' \n').encode())
                    self.JOINED = True

                line_array = line.split()
                user_and_mask = line_array[0][1:]
                usr = user_and_mask.split("!")[0]
                channel = line_array[2]
                try:
                    message = line.split(":", 2)[2]
                    self.brain.respond(usr, channel, message)
                except IndexError:
                    try:
                        message = line.split(":", 2)[1]
                        self.brain.respond(usr, channel, message)
                    except IndexError:
                        print(("index out of range.", line))

        except Exception:
            print(("Unexpected error:", sys.exc_info()[0]))
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

        # we have to cast it to an int, otherwise the connection fails silently
        # and the entire process dies
        try:
            self.PORT = int(self.conf.getPort(self.network))
        except AttributeError:
            self.PORT = 6667
        self.IDENT = 'mypy'
        self.REALNAME = 's1ash'
        if not self.OWNER:
            self.OWNER = self.conf.getOwner(self.network)

        # connect to server
        self.s = socket.socket()
        while not self.CONNECTED:
            try:
                if self.DEBUG:
                    self.debug_print(util.bcolors.YELLOW +
                                     ">>" +
                                     util.bcolors.ENDC +
                                     " attempting to connect to " +
                                     self.network +
                                     ":" +
                                     str(self.PORT))
                    self.debug_print(
                        util.bcolors.GREEN +
                        ">>" +
                        util.bcolors.ENDC +
                        " owner: " +
                        self.OWNER)
# low level socket TCP/IP connection
                # force them into one argument
                self.s.connect((self.HOST, self.PORT))
                self.CONNECTED = True
                self.logger.write(
                    Logger.INFO,
                    "Connected to " +
                    self.network,
                    self.NICK)
                if self.DEBUG:
                    self.debug_print(util.bcolors.YELLOW +
                                     ">> " +
                                     util.bcolors.ENDC +
                                     "connected to " +
                                     self.network +
                                     ":" +
                                     str(self.PORT))
            except BaseException:
                if self.DEBUG:
                    self.debug_print(util.bcolors.FAIL +
                                     ">> " +
                                     util.bcolors.ENDC +
                                     "Could not connect to " +
                                     self.HOST +
                                     " at " +
                                     str(self.PORT) +
                                     "! Retrying... ")
                self.logger.write(Logger.CRITICAL, "Could not connect to " +
                                  self.HOST + " at " + str(self.PORT) + "! Retrying...")
                time.sleep(1)

                self.worker()

            time.sleep(1)
        # core IRC protocol stuff
            self.s.send(('NICK ' + self.NICK + '\n').encode())

            if self.DEBUG:
                self.debug_print(util.bcolors.YELLOW + ">> " + util.bcolors.ENDC +
                                 self.network + ': NICK ' + self.NICK + '\\n')

            self.s.send(
                ('USER ' +
                 self.IDENT +
                 ' 8 ' +
                 ' bla : ' +
                 self.REALNAME +
                 '\n').encode())  # yeah, don't delete this line

            if self.DEBUG:
                self.debug_print(
                    util.bcolors.YELLOW +
                    ">> " +
                    util.bcolors.ENDC +
                    self.network +
                    ": USER " +
                    self.IDENT +
                    ' 8 ' +
                    ' bla : ' +
                    self.REALNAME +
                    '\\n')

            time.sleep(3)  # allow services to catch up

            try:
                self.s.send(
                    ('PRIVMSG nickserv identify ' +
                     self.conf.getIRCPass(
                         self.network) +
                        '\n').encode())  # we're registered!
                if self.DEBUG:
                    self.debug_print(util.bcolors.YELLOW + ">> " + util.bcolors.ENDC + self.network +
                                     ': PRIVMSG nickserv identify ' + self.conf.getIRCPass(self.network) + '\\n')
            except AttributeError:
                # we're registered!
                self.s.send(('PRIVMSG nickserv identify 12345 \n').encode())
                if self.DEBUG:
                    self.debug_print(
                        util.bcolors.YELLOW +
                        ">> " +
                        util.bcolors.ENDC +
                        self.network +
                        ': PRIVMSG nickserv identify 12345 \\n')

        self.s.setblocking(1)

        read = ""

        timeout = 0

# does not require a definition -- it will be invoked specifically when
# the bot notices it has been disconnected
        disconnect_event = Event("__.disconnection__")
#   if we're only running a test of connecting, and don't want to loop forever
        if mock:
            return
        # infinite loop to keep parsing lines
        while True:
            try:
                timeout += 1
                # if we haven't received anything for 120 seconds
                try:
                    time_since = self.conf.getTimeout(self.network)
                except AttributeError:
                    time_since = 120
                if timeout > time_since:
                    if self.DEBUG:
                        self.debug_print("Disconnected! Retrying... ")
                    disconnect_event.notifySubscribers("null")
                    self.logger.write(
                        Logger.CRITICAL, "Disconnected!", self.NICK)
# so that we rejoin all our channels upon reconnecting to the server
                    self.JOINED = False
                    self.CONNECTED = False

                    global RETRY_COUNTER
                    if RETRY_COUNTER > 10:
                        self.debug_print(
                            "Failed to reconnect after 10 tries. Giving up...")
                        sys.exit(1)

                    RETRY_COUNTER += 1
                    self.worker()

                time.sleep(1)
                ready = select.select([self.s], [], [], 1)
                if ready[0]:
                    try:
                        read = read + \
                            self.s.recv(1024).decode('utf8', 'ignore')
                    except UnicodeDecodeError as e:
                        self.debug_print(
                            "Unicode decode error; " + e.__str__())
                        self.debug_print("Offending recv: " + self.s.recv)
                    except Exception as e:
                        print(e)
                        if self.DEBUG:
                            self.debug_print("Disconnected! Retrying... ")
                        disconnect_event.notifySubscribers("null")
                        self.logger.write(
                            Logger.CRITICAL, "Disconnected!", self.NICK)
                        self.JOINED = False
                        self.CONNECTED = False
                        self.worker()

                    lines = read.split('\n')

                    # Important: all lines from irc are terminated with '\n'. lines.pop() will get you any "to be continued"
                    # line that couldn't fit in the socket buffer. It is stored
                    # and tacked on to the start of the next recv.
                    read = lines.pop()

                    # an empty array evaluates to False
                    if lines:
                        timeout = 0

                    for line in lines:
                        line = line.rstrip()
                        self.processline(line)
            except KeyboardInterrupt:
                print("keyboard interrupt caught; exiting ...")
                raise

    # end worker

    def debug_print(self, line, error=False):
        """
        Prepends incoming lines with the current timestamp and the thread's name, then spits it to stdout.
        Warning: this is entirely asynchronous between threads. If you connect to multiple networks, they will interrupt each other between lines.  #

        Args:
        line: text.
        error: boolean, defaults to False. if True, prints out with red >> in the debug line
        """

        if not error:
            print((str(datetime.datetime.now()) + ": " +
                  self.getName() + ": " + line.strip('\n').rstrip().lstrip()))
        else:
            print((str(datetime.datetime.now()) +
                   ": " +
                   self.getName() +
                   ": " +
                   util.bcolors.FAIL +
                   ">> " +
                   util.bcolors.ENDC +
                   line.strip('\n').rstrip().lstrip()))

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
