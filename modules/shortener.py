import urllib2
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
        url = "http://is.gd/create.php?format=simple&url=" + target 
        response = urllib2.urlopen(url)
        self.printer("PRIVMSG " + event.channel + " :" + response.read() + '\n')

    except:
      pass
