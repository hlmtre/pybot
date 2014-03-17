import re
import urllib2
from urlparse import urlparse, parse_qsl
from xml.dom.minidom import parseString
from datetime import datetime, timedelta
class Youtube:
  def __init__(self, events=None, printer_handle=None, bot=None):
    self.events = events
    self.printer = printer_handle
    self.bot = bot
    self.interests = ['__youtubes__']
    for event in events:
      if event._type in self.interests:
        event.subscribe(self)

  def handle(self, event):
    try:
      url = re.search("youtube.com[\S]+", event.line).group(0)
      if url:
        get_dict = dict(parse_qsl(urlparse(url).query)) # create dictionary of strings, instead of of lists. this fails to handle if there are multiple values for a key in the GET
        video_tag = get_dict['v']
        if video_tag.__len__() > 1:
          response = urllib2.urlopen("https://gdata.youtube.com/feeds/api/videos/"+video_tag+"?v=2").read()
          xml_response = parseString(response)
          duration = xml_response.getElementsByTagName('yt:duration')
          ulength = duration[0].getAttribute("seconds")
          alength = ulength.encode('ascii', 'ignore')
          length = str(timedelta(seconds=int(alength)))
          titletag = xml_response.getElementsByTagName('title')[0]
          video_title = titletag.childNodes[0].nodeValue
          self.printer("PRIVMSG " + event.channel + " :YouTube: " + video_title + " ("+length+")\n")
        else:
          pass
          #print "error!"
    except TypeError:
      pass
