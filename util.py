import re
from datetime import datetime
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
    def __init__(self):
      self.first_word = None
      self.message = None
      self.channel = None
      self.user = None
      self.message_number = 0

    def startswith(self, thing):
      if self.message.startswith(thing):
        return True
      return False

  parsed = Parsed()

  try:
    parsed.message_number = line.split()[1]
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
  second_diff = diff.seconds
  day_diff = diff.days

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
    return "yesterday"
  if day_diff < 7:
    return str(day_diff) + " days ago"
  if day_diff < 31:
    return str(day_diff/7) + " weeks ago"
  if day_diff < 365:
    return str(day_diff/30) + " months ago"
  return str(day_diff/365) + " years ago"
