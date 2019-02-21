from random import randint
from util import commands

@commands(".d8")
def d4(bot, message, channel):
  bot.say(channel, str(randint(1,8)))
