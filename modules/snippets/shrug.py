from random import randint
from util import commands


@commands(".shrug")
def shrug(bot, message, channel):
    bot.say(channel, "¯\\_(ツ)_/¯")
