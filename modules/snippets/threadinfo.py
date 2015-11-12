from util import commands

@commands(".threadinfo")
def thread_info(bot, message, channel):
  threads = bot.blist.get()
  print threads
  for t in threads:
    print dir(t)
