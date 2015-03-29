#!/usr/bin/env python

import signal
import sys
import time

def killhandle(signum,frame):
  print "caught SIGTERM"
  sys.exit(0)

def nodie(signum,frame):
  print "no"

signal.signal(signal.SIGTERM, killhandle)
signal.signal(signal.SIGINT, nodie)

while 1:
  print "."
  time.sleep(1)
