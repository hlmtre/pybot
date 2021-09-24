import sys
from util import commands
from util import parse_line
from logger import Logger
import imp


@commands(".reflect")
def reflect_reload(bot, message, channel):
    logger = bot.logger
    parse_line(message)
    # for k,v in parsed.__dict__.iteritems():
    #  print k, ": ", v
    body = message.split(":")[2:]
    recomposed = "".join(body)
    if recomposed.startswith(".reflect reload"):
        for m in recomposed.split()[2:]:
            if m in sys.modules:
                try:
                    imp.reload(sys.modules[m])
                    bot.brain.notice(channel, 'reloaded ' + m)
                    logger.write(
                        Logger.INFO,
                        bot.getName() +
                        ": reloaded " +
                        m,
                        bot.NICK)
                except ImportError as e:
                    bot.brain.notice(channel, 'failed to reload ' + m)
                    logger.write(
                        Logger.CRITICAL,
                        bot.getName() +
                        ": failed to reload " +
                        m,
                        bot.NICK)
                    logger.write(
                        Logger.CRITICAL,
                        bot.getName() +
                        ": error was:",
                        bot.NICK)
                    logger.write(
                        Logger.CRITICAL,
                        bot.getName() + ": " + e,
                        bot.NICK)
                    return
