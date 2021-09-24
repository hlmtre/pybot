from util import commands
from util import parse_line
import sys
from logger import Logger


@commands(".snippet", ".snippets")
def reload(bot, message, channel):
    logger = bot.logger
    parsed = parse_line(message)
    if parsed.startswith(".snippets reload"):
        try:
            bot.load_snippets()
            bot.set_snippets()
            bot.brain.notice(channel, "snippets reloaded")
        except BaseException:
            e = sys.exc_info()[0]
            logger.write(
                Logger.WARNING,
                bot.getName() +
                ": failed to reload snippets",
                bot.NICK)
            logger.write(
                Logger.WARNING,
                bot.getName() +
                ": error was:",
                bot.NICK)
            logger.write(Logger.WARNING, bot.getName() + ": " + e, bot.NICK)
