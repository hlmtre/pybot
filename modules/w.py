import shelve
try:
  from weather_util import api_request, get_results
except ImportError:
  from modules.weather_util import api_request, get_results

from event import Event
try:
    from basemodule import BaseModule
except ImportError:
    from modules.basemodule import BaseModule
try:
    from weather2 import api_request
except ImportError:
    from modules.weather2 import api_request

class W(BaseModule):
  def post_init(self):
    w = Event('__.w__')
    w.define(msg_definition='^\.w')
    w.subscribe(self)

  def add_to_shelve(self, username, zipcode):
    d = selve.open("./w_persist")
    d[username] = zipcode
    d.close()

  def get_zip(self, username):
    d = shelve.open("./w_persist")
    if username in d:
      return d[username]

  def call_weather(self, zipcode):
    query = api_request(weather_line[1], event.channel)
    if not query:
      return
    weather = get_conditions(query, event.channel)
    if not weather:
      return
    return weather
     

  def handle(self, event):
    w_line = event.msg.split(None, 1)
    if w_line[1] == "add":
      self.add_to_shelve(w_line[2], w_line[3]) # should be in format .w add hlmtre 95969
      return
    if len(w_line) == 1:
      self.say(event.channel, self.call_weather(self.get_zip(event.user)))
      return



