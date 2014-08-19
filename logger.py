import datetime
import time
import inspect
import sys
class Logger:
  CRITICAL, WARNING, INFO = range(3)
  levels = ['CRITICAL', 'WARNING', 'INFO']

  def write(self, level, line, nick=None):
    if nick is not None:
      n = nick
    else:
      n = 'pylog'
    try: 
      f = open(n+'-'+str(time.strftime("%m-%d-%Y"))+'.log', "a")
      f.write(str(datetime.datetime.now())+ " (" + inspect.stack()[1][3] + ") " + str(Logger.levels[level]) + ": " + line + '\n')
    except IOError:
      pass
