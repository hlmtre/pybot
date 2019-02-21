from random import randint
from util import commands

@commands(".d10")
def d10(bot, message, channel):
  bot.say(channel, str(randint(1,10)))
