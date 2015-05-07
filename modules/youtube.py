import re
import urllib2
import json
from urlparse import urlparse, parse_qsl
from xml.dom.minidom import parseString
from datetime import datetime, timedelta
from collections import OrderedDict
import time
import logger
from event import Event

try:
  import isodate
except ImportError:
  print "WARNING: youtube module now requires isodate (thanks, ISO8601)"

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


    # for the new v3 google api >:(
    self.api_key = "AIzaSyDwzB3Sf_E-7VyKZYWXP9DjjlnPBs5kSfc"
    self.api_url = "https://www.googleapis.com/youtube/v3/videos?id="
    #self.api_url = "https://www.googleapis.com/youtube/v3/videos?id=2k_9mXpNdgU&key=&part=snippet"

  def print_video_title(self, event, url, video_tag):
    if event.user == self.bot.conf.getNick(self.bot.network): #ignore himself
      return
    if event.msg.startswith("YouTube:"):
      return
    try:
      response = urllib2.urlopen(self.api_url+video_tag+"&key="+self.api_key+"&part=contentDetails,snippet").read()
    except urllib2.HTTPError:
      return

    try:
      jsonified = json.loads(response)["items"][0]
    except IndexError, e:
      self.bot.logger.write(Logger.WARNING, "IndexError pulling youtube videos. Zero results for: ")
      self.bot.logger.write(Logger.WARNING, url)
      return

    duration_string = jsonified['contentDetails']['duration']
    title = jsonified['snippet']['title']

    if isodate:
      duration = isodate.parse_duration(duration_string)
    else:
      duration = dict()
      duration['seconds'] = 00

    self.say(event.channel, "YouTube: \"" + title + "\" (" + time.strftime("%H:%M:%S", time.gmtime(duration.seconds)) + ")")
    return 

  def handle(self, event):
#   prevent bot from printing youtube information if a youtube link is in the channel topic (or elsewhere that isn't a message to a channel)
    if "PRIVMSG" not in event.line:
      return
    if event._type == "__.youtubes__":
      url = re.search("youtube.com[\S]+", event.line).group(0)
      try:
        get_dict = dict(parse_qsl(urlparse(url).query)) # create dictionary of strings, instead of of lists. this fails to handle if there are multiple values for a key in the GET
        video_tag = get_dict['v']
      except KeyError:
        return
    elif event._type == "__.youtubeshort__":
      url = re.search("youtu\.be[\S]+", event.line).group(0)
      if url: 
        video_tag = url.split("/")[-1]
        if "?" in video_tag:
          video_tag = video_tag.split("?")[0]
      else:
        return
    if url and video_tag.__len__() > 1:
      self.print_video_title(event, url, video_tag)
