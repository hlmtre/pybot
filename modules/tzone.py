##Simple module to spit out the time in a certain area/timezone, poorly thrown together by mech##

"""More to come, add some regex in and make it easier to find the timezone without being super specific"""


import os, time, sys
from event import Event
try:
  import pytz
except (ImportError, SystemError):
  print("tzone requires pytz pip module")
  pytz = None


try:
  if sys.version_info > (3, 0, 0):
    from .basemodule import BaseModule
  else:
    from basemodule import BaseModule
except (ImportError, SystemError):
  from modules.basemodule import BaseModule

class Tzone(BaseModule):
  def post_init(self):
    tzone = Event("__.tzone__")
    tzone.define(msg_definition="^\.tzone")
    tzone.subscribe(self)
    self.cmd = ".tzone"
    self.help = ".tzone <Insert timezone> timezones: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"

    self.bot.register_event(tzone, self)

  def handle(self, event):
    if pytz == None:
      print("tzone requires pytz pip module")
      return

    lower_list = []  #Empty list for TZ list with no capitalization
    tz_list = pytz.all_timezones #List of all available timezones
    try:
      if event.msg.startswith(".tzone"): #Splits the option from the ".tzone" command to be used to find the proper timezone
        split_tz = event.msg.split()
        tz = split_tz[1].lower()

        for x in pytz.all_timezones: #Adds all timezones with no capitalization so the user will not have to worry about that
          lower_list.append(x.lower())

        ll_index = lower_list.index(tz) #Grabs the index number of the timezone requested to be applied to the main timezone list

        if tz not in lower_list: #If the timezone requested is not in the lower list it will spit this out
          self.say(event.channel, "This is not a valid timezone option, timezone options: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")
        else:
          os.environ['TZ'] = tz_list[ll_index] #If the timezone is found in the lower list it will be fed into here to spit out the local time
          time.tzset()
          tz_time = time.strftime('%X %x %Z') #The format in which the time is printed out
          self.say(event.channel, tz_time)
    except IndexError: #Handles the 2 errors I have found based on user error
      self.say(event.channel, "Idk what your did, but it was wrong")
    except ValueError:
        self.say(event.channel, "Not a valid timezone, .tzone <insert timezone>, timezone options: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")
