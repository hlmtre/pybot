#!/usr/bin/env python2

import argparse, os, sys, time
import confman, util, logger, bot

if __name__ == "__main__":
  DEBUG = False

  parser = argparse.ArgumentParser(description="a python irc bot that does stuff")
  parser.add_argument('config', nargs='?')
  parser.add_argument('-d', help='debug (foreground) mode', action='store_true')

  args = parser.parse_args()
  if args.d:
    DEBUG = True
  if args.config:
    config = args.config
  else:
    config = "~/.pybotrc"

  botslist = list()
  if not DEBUG and hasattr(os, 'fork'):
    pid = os.fork()
    if pid == 0: # child
      if os.name == "posix":
        print "starting bot in the background, pid " + util.bcolors.GREEN + str(os.getpid()) + util.bcolors.ENDC
      else:
        print "starting bot in the background, pid " + str(os.getpid())

      cm = confman.ConfManager(config)
      net_list = cm.getNetworks()
      for c in cm.getNetworks():
        b = bot.Bot(cm, c, DEBUG)
        b.start()

    elif pid > 0:
      sys.exit(0)
  else: # don't background; either we're in debug (foreground) mode, or on windows TODO
    if os.name == 'nt':
      print 'in debug mode; backgrounding currently unsupported on windows.'
    DEBUG = True
    print "starting bot, pid " + util.bcolors.GREEN + str(os.getpid()) + util.bcolors.ENDC
    try:
      f = open(os.path.expanduser(config))
    except IOError:
      print "Could not open conf file " + config
      sys.exit(1)

    cm = confman.ConfManager(config)
    net_list = cm.getNetworks()
    for c in cm.getNetworks():
      b = bot.Bot(cm, c, DEBUG)
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
        b.s.send("QUIT :because I got killed\n")
      print
      print "keyboard interrupt caught; exiting"
      sys.exit(1)
