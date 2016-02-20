import platform
import socket

from util import commands
import version

@commands(".platform")
def platform_info(bot, message, channel):
  bot.say(channel, "I'm " + bot.NICK + ", running on python version " + platform.python_version() + ", on " + socket.getfqdn())  
