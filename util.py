import re
class bcolors:
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
  nick = re.sub('[@~+]', '', nick)
  return nick
