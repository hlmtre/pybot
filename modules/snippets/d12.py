from random import randint
from util import commands


@commands(".d12")
def d12(bot, message, channel):
    bot.say(channel, str(randint(1, 12)))
