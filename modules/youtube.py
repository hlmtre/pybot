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
    youtube.define(msg_definition="youtube\.com[\S]+")
    youtube2 = Event("__.youtubeshort__")
    youtube2.define(msg_definition="(?<!=)youtu\.be[\S]+")
    youtube.subscribe(self)
    youtube2.subscribe(self)

    self.bot.register_event(youtube, self)
    self.bot.register_event(youtube2, self)

    self.bot.mem_store['youtube'] = OrderedDict()

  def print_video_title(self, event, url, video_tag):
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

  def handle(self, event):
    if event._type == "__.youtubes__":
      url = re.search("youtube.com[\S]+", event.line).group(0)
      try:
        get_dict = dict(parse_qsl(urlparse(url).query)) # create dictionary of strings, instead of of lists. this fails to handle if there are multiple values for a key in the GET
        video_tag = get_dict['v']
      except KeyError:
        pass
    elif event._type == "__.youtubeshort__":
      url = re.search("youtu\.be[\S]+", event.line).group(0)
      video_tag = url.split("/")[-1]
    if not url:
      print "No url found."
    if url and video_tag.__len__() > 1:
      self.print_video_title(event, url, video_tag)
