import datetime
import time
import inspect
import sys
class Logger:
  CRITICAL, WARNING, INFO = range(3)
  levels = ['CRITICAL', 'WARNING', 'INFO']

  def write(self, level, line):
    try: 
      f = open('pylog-'+str(time.strftime("%d-%m-%Y"))+'.log', "a")
      f.write(str(datetime.datetime.now())+ " (" + inspect.stack()[1][3] + ") " + str(Logger.levels[level]) + ": " + line + '\n')
    except IOError:
      pass
