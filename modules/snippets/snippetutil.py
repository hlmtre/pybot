from util import commands
from util import parse_line
import inspect

@commands(".snippet", ".snippets")
def reload(bot, message, channel):
  parsed = parse_line(message)
  if parsed.startswith(".snippet reload"):
    try:
      bot.load_snippets()
      bot.set_snippets()
      bot.brain.notice(channel, "snippets reloaded")
    except:
      pass
