import datetime
import time
import inspect
import sys
import os
class Logger:
  CRITICAL, WARNING, INFO = range(3)
  levels = ['CRITICAL', 'WARNING', 'INFO']

  def write(self, level, line, nick=None, location=None):
    if location is not None:
      l = location
    else:
      l = "~/"
    if nick is not None:
      n = nick
    else:
      n = 'pylog'

    try: 
      f = open(os.path.expanduser(l + n + '-'+str(time.strftime("%m-%d-%Y")))+'.log', "a")
      f.write(str(datetime.datetime.now())+ " (" + inspect.stack()[1][3] + ") " + str(Logger.levels[level]) + ": " + line + '\n')
    except IOError:
      pass
