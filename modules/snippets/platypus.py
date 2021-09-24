import platform
import socket

from util import commands
import version


@commands(".platform", ".platypus")
def platform_info(bot, message, channel):
    unique_modules = set()
    # because the bot doesn't necessarily hold onto modules themselves, just events, iterate over the events, and then all their subscribers.
    # then unique off those.
    for ev in bot.events_list:
        for x in ev.subscribers:
            unique_modules.add(type(x).__name__)
    bot.say(channel, "I'm " +
            bot.NICK +
            " v. " +
            version.__version__ +
            ", running on python " +
            platform.python_version() +
            ", on " +
            socket.getfqdn() +
            ". I have " +
            str(len(unique_modules)) +
            " modules loaded.")
