from random import randint
from util import commands

@commands(".d4")
def d4(bot, message, channel):
  bot.say(channel, str(randint(1,4)))
