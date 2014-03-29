import re
import urllib2
from urlparse import urlparse, parse_qsl
from xml.dom.minidom import parseString
from datetime import datetime, timedelta
from collections import OrderedDict
from event import Event

try:
  from modules.basemodule import BaseModule
except ImportError:
  from basemodule import BaseModule
class Youtube(BaseModule):
  def post_init(self):
    youtube = Event("__.youtubes__")
    youtube.define(msg_definition="youtube.com[\S]+")
    youtube.subscribe(self)

    self.bot.register_event(youtube, self)

    self.bot.mem_store['youtube'] = OrderedDict()

  def handle(self, event):
    url = re.search("youtube.com[\S]+", event.line).group(0)
    if url:
      get_dict = dict(parse_qsl(urlparse(url).query)) # create dictionary of strings, instead of of lists. this fails to handle if there are multiple values for a key in the GET
      try:
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
          self.say(event.channel, "Youtube: " + video_title + " ("+length+")")
          self.bot.mem_store['youtube'][video_title] = url
        else:
          pass
      except KeyError:
        pass
