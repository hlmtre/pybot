from random import randint
from util import commands

@commands(".d6")
def d4(bot, message, channel):
  bot.say(channel, str(randint(1,6)))
