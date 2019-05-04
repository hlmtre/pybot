import platform
import socket

from util import commands
import version

@commands(".platform")
def platform_info(bot, message, channel):
  bot.say(channel, "I'm " + bot.NICK + " v. " + version.__version__ + ", running on python " + platform.python_version() + ", on " + socket.getfqdn() + ". I have " + str(len(bot.loaded_modules)) + " modules loaded.")
  print bot.loaded_modules
