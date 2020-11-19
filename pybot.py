#!/usr/bin/env python3

if __name__ == "__main__":
  import argparse
  import os
  import sys
  import time

  import bot
  import confman
  import logger
  import util
  DEBUG = False

  parser = argparse.ArgumentParser(description="a python irc bot that does stuff")
  group = parser.add_mutually_exclusive_group()
  group.add_argument('--config', '-c', nargs=1, help='path to config file (/your/path/to/pybotrc)', default=None)
  group.add_argument('--nick', '-n', nargs=1, help='bot\'s irc nickname', default=None)
  parser.add_argument('--server', '-s', nargs=1, help='server to connect to (irc.yourserver.com)', default=None)
  parser.add_argument('--channels', nargs=1, help='channels to join ("#channel1, #channel2")', default=None)
  parser.add_argument('--debug', '-d', help='debug (foreground) mode', action='store_true')

  args = parser.parse_args()
  if args.debug:
    DEBUG = True
  if args.config:
    config = args.config[0]
  else:
    config = "~/.pybotrc"

  if args.nick or args.server or args.channels:
    config = None

  botslist = list()
  if not DEBUG and hasattr(os, 'fork'): # are we on a system that can fork()?
    pid = os.fork()
    if pid == 0: # child
      if os.name == "posix":
        print("starting bot in the background, pid " + util.bcolors.GREEN + str(os.getpid()) + util.bcolors.ENDC)
      else:
        print("starting bot in the background, pid " + str(os.getpid()))

      if not config:
        b = bot.Bot(network=args.server[0], local_nickname=args.nick[0], local_channels=args.channels[0])
        b.start()
      else:
        cm = confman.ConfManager(config)
        net_list = cm.getNetworks()
        for c in cm.getNetworks():
          b = bot.Bot(cm, c, DEBUG)
          b.start()

    elif pid > 0:
      sys.exit(0)
  else:  # don't background; either we're in debug (foreground) mode, or on windows
    if os.name == 'nt':
      print('in debug mode; forking unsupported on windows.')
    DEBUG = True
    print("starting bot, pid " + util.bcolors.GREEN + str(os.getpid()) + util.bcolors.ENDC)
    if not config:
      b = bot.Bot(d=True, network=args.server[0], local_nickname=args.nick[0], local_channels=args.channels[0])
      b.daemon = True
      b.start()
      botslist.append(b)
    else:
      try:
        f = open(os.path.expanduser(config))
      except IOError:
        print("Could not open conf file " + config)
        sys.exit(1)

    if config:
      cm = confman.ConfManager(config)
      net_list = cm.getNetworks()
      for c in cm.getNetworks():
        b = bot.Bot(conf=cm, network=c, d=DEBUG)
        b.daemon = True
        b.start()
        botslist.append(b)
    try:
      while True:
        time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
      l = logger.Logger()
      l.write(logger.Logger.INFO, "killed by ctrl+c or term signal")
      for b in botslist:
        b.save_persistence()
        b.s.send(("QUIT :because I got killed\n").encode())
      print()
      print("keyboard interrupt caught; exiting")
      sys.exit(1)
