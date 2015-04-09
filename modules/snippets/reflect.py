import sys
from util import commands

@commands(".reflect")
def reflect_reload(bot, message, channel):
  body = message.split(":")[2:]
  recomposed = "".join(body)
  if recomposed.startswith(".reflect reload"):
    for m in recomposed.split()[2:]:
      if m in sys.modules:
        reload(sys.modules[m])
        bot.brain.notice(channel, 'reloaded ' + m)
