#Youtube module 2.0 updated to use requests

import sys, re, json
import time
import logger
from event import Event
from collections import OrderedDict
from urllib.parse import urlparse, parse_qsl

try:
  import requests
except (ImportError, SystemError):
  print("Warning: youtube module requires requests")
  requests = object

try:
  if sys.version_info > (3, 0, 0):
    from .basemodule import BaseModule
  else:
    from basemodule import BaseModule
except (ImportError, SystemError):
  from modules.basemodule import BaseModule

try:
  import isodate
except (ImportError, SystemError):
  print("WARNING: youtube module now requires isodate (thanks, ISO8601)")

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
    try:
      from youtube_credentials import YoutubeCredentials as yc
    except (ImportError, SystemError):
      print("Warning: youtube module requires credentials in modules/youtube_credentials.py")
      class PhonyYc:
        api_key = "None"
      yc = PhonyYc()

    self.api_key = yc.api_key
    self.url = "https://www.googleapis.com/youtube/v3/videos?id="
  
  def print_video_title(self, event, url, video_tag):
    headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            }
    if event.user == self.bot.conf.getNick(self.bot.network): #ignore himself
      return
    if event.msg.startswith("YouTube:"):
      return
    try:
      response = requests.get(url + video_tag + "&key=" + self.api_key + "&part=contentDetails,snippet", headers=headers)
    except requests.exceptions.HTTPError:
      return
    try:
      jsonified = json.loads(response.text) #Converts our JSON to Python object
      duration_string = jsonified["items"][0]["contentDetails"]["duration"]
      vid_title = jsonified["items"][0]["snippet"]["title"]
    except IndexError as e:
      self.bot.logger.write(logger.Logger.WARNING, "IndexError pulling youtube videos. Zero results for: ")
      self.bot.logger.write(logger.Logger.WARNING, url)
      return
    

    if isodate:
      duration = isodate.parse_duration(duration_string)
    else:
      duration = dict()
      duration['seconds'] = 00
    
    self.say(event.channel, "YouTube: \"" + vid_title + "\" (" + time.strftime("%H:%M:%S", time.gmtime(duration.seconds)) + ")")
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
      self.print_video_title(event, self.url, video_tag)