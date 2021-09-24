import datetime
import inspect
import os
import sys
import time


class Logger:
    CRITICAL, WARNING, INFO = list(range(3))
    levels = ['CRITICAL', 'WARNING', 'INFO']

    def write(self, level, line, nick=None, location=None):
        """
        Write out to the logfile of either default location or otherwise specified.
        Includes calling class in its logged line.

        Args:
        level: enumerated thing from the logger class.
        line: string. thing to write out to the logger.
        nick: string. determines filename.
        location: where to write the logfile out to.

        Returns:
        nothing.

        """
        if location is not None:
            l = location
        else:
            l = "~/"
        if nick is not None:
            n = nick
        else:
            n = 'pylog'

        try:
            if not os.path.exists(os.path.expanduser(l + '/logs/')):
                os.makedirs(os.path.expanduser(l + '/logs'))
            f = open(os.path.expanduser(l + '/logs/' + n + '-' +
                     str(time.strftime("%m-%d-%Y"))) + '.log', "a")
            if sys.version_info > (3, 0, 0):
                f.write(str(datetime.datetime.now())
                        + " (" + inspect.getframeinfo(inspect.stack()
                                                      [1][0]).filename
                        + ":" +
                        str(inspect.getframeinfo(inspect.stack()[1][0]).lineno)
                        + " <" + inspect.stack()[1][3] +
                        ">) " + str(Logger.levels[level])
                        + ": " + line + '\n')
            else:
                f.write(str(datetime.datetime.now()) +
                        " (" +
                        inspect.stack()[1][3] +
                        ") " +
                        str(Logger.levels[level]) +
                        ": " +
                        line +
                        '\n')
        except IOError as e:
            print("IO Error!")
            print(e)
        except OSError:
            print("probably permission denied.")
