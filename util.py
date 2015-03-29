import re
import os
import sys
class bcolors:
  """
  Allows for prettyprinting to the console for debugging.
  """
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  CYAN = '\033[36m'
  GREEN = '\033[32m'
  YELLOW = '\033[33m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'

def set_exit_handler(func):
  import signal
  signal.signal(signal.SIGTERM, func)

def on_exit(sig, frame):
  print "caught '%s'" % sig
  rmPid()
  os.killpg(0,sig)
  sys.exit(0)

def writePid(pid):
  """
    Writes out a pidfile to /tmp/pybot/run. Does not touch /tmp/pybot; you can use this for other things that are temporary but needed.
  """
  nick = "pybot" # perhaps TODO? do we want a pidfile always named pybot.pid, or $YOUR_CHOSEN_NICK.pid?
  path = "/tmp/" + nick + "/run/"
  if not os.path.exists(path):
    os.makedirs(path)
  #if os.path.isdir(path):
  #  if os.path.exists(path): # pidfile already exists, simply (truncate and) update its contents
  pidfile = open(path + nick + ".pid", "w")
  pidfile.write(pid)

def rmPid():
  nick = "pybot"
  try:
    os.remove("/tmp/" + nick + "/run/" + nick + ".pid")    
  except OSError:
    print "WARNING: could not remove " + nick + ".pid. This may or may not be startling."
    return

def strip_nick(nick):
  """
  Clean up nicks of their op levels (&Schooly_D, ~BoneKin, etc)
  """
  nick = re.sub('[@~+]', '', nick)
  return nick

def depends(self, module_name):
  for m in self.loaded_modules:
    if m.__class__.__name__ == module_name:
      return m
  return None

def commands(*command_list):
  def add_attribute(function):
    if not hasattr(function, "commands"):
      function.commands = []
    function.commands.extend(command_list)
    return function
  return add_attribute

def parse_line(line):
  """
  returns an object with a nice set of line-pulled-apart members
  """
  class Parsed():
    def __init(self):
      self.first_word = None
      self.message = None
      self.channel = None
      self.user = None

    def startswith(self, thing):
      if self.message.startswith(thing):
        return True
      return False

  parsed = Parsed()

  try:
    parsed.first_word = line.split(":", 2)[2]
    parsed.message = line.split(":",2)[2]
    parsed.channel = line.split()[2]
    if "JOIN" in line or "QUIT" in line:
      parsed.user = line.split("!")[0].replace(":","")
    else:
      parsed.user = line.split(":")[1].rsplit("!")[0] # nick is first thing on line
  except IndexError:
    return None
  else:
    return parsed

def __prettyDate(time):
  """
  Similar to Rails's nice time since thing.
  """
  now = datetime.now()
  if type(time) is int:
    diff = now - datetime.fromtimestamp(time)
  elif isinstance(time,datetime):
    diff = now - time 
  elif not time:
    diff = now - now
  second_diff = diff.seconds
  day_diff = diff.days

  if day_diff < 0:
    return ''

  if day_diff == 0:
    if second_diff < 10:
      return "just now"
    if second_diff < 60:
      return str(second_diff) + " seconds ago"
    if second_diff < 120:
      return  "a minute ago"
    if second_diff < 3600:
      return str( second_diff / 60 ) + " minutes ago"
    if second_diff < 7200:
      return "an hour ago"
    if second_diff < 86400:
      return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
      return "Yesterday"
    if day_diff < 7:
      return str(day_diff) + " days ago"
    if day_diff < 31:
      return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
      return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago"
