import requests
import re
class Shortener:
  def __init__(self, events=None, printer_handle=None, bot=None, say=None):
    self.events = events
    self.printer = printer_handle
    self.interests = ['__urls__']
    self.bot = bot
    self.say = say

    self.cmd = None
    self.help = "url shortening utility function"

    for event in events:
      if event._type in self.interests:
       # print "DEBUG: registering to ",
       # print event
        event.subscribe(self)

  def handle(self, event):
    try:
      target = re.search("https?://[\S]+", event.line).group(0)
      if len(target) > 60:
        url = 'https://is.gd/create.php'
        payload = {'format':'simple', 'url':target}
        r = requests.get(url, params=payload)
        self.say(event.channel, r.text)

    except requests.exceptions.HTTPError as e:
      self.bot.debug_print("HTTPError")
      self.bot.debug_print(str(e))

