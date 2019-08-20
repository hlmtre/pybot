# -*- coding: utf-8 -*-
import sys
import os
from collections import defaultdict
import webwriter
import time
import logger
import datetime
if sys.version_info > (3,0,0):
  import urllib.request, urllib.error, urllib.parse
  from urllib.parse import urlparse, parse_qsl
else:
  import urllib2
  from urlparse import urlparse, parse_qsl
import json
import re
from xml.dom.minidom import parseString
from datetime import datetime, timedelta
import lite

class BotBrain:
  BRAINDEBUG = False

  def __init__(self, microphone, bot=None):

    self.microphone = microphone
    self.bot = bot
    yth = dict()
    self.db = self.bot.db
    self.ww = webwriter.WebWriter()

  def _isAdmin(self, username):
    if self.bot.conf.getOwner(self.bot.network) == username:
      return True
    if self.db.isAdmin(username):
      return True
    return False

  def getMicrophone(self):
    return self.microphone

  def _updateSeen(self, user, statement, event):
    self.db.updateSeen(user, statement, event)

  def _insertImg(self, user, url, channel):
    self.db.insertImg(user, url, channel)

  def __bareSay(self, thing):
    self.microphone(thing + '\n')

  def say(self, channel, thing):
    try:
      s = thing.encode('utf-8', 'ignore')
    except UnicodeEncodeError as e:
      print(e)
      print(thing)
      return None
    except UnicodeDecodeError as d:
      print(d)
      print(thing)
      return None

    outstring = 'PRIVMSG ' + channel + ' :' + s.decode('utf-8','ignore') + '\n'
    self.microphone(outstring)

  def notice(self, channel, thing):
    self.microphone('NOTICE ' + channel + ' :' + str(thing) + '\n')

  def _speak(self, user, target, message):
    if target.startswith("#"):
      self.say(target, message) 
    else:
      target = "#" + target
      self.say(target, message)

  def _onstat(self, channel):
    self.say(channel, "Yep, I'm on. Idiot.")

  def _join(self, usr, message):
    if self._isAdmin(usr):
      if len(message.split()) is 3:
        channel = message.split()[1]
        extraArg = message.split()[-1]
        self.__bareSay("JOIN " + channel + " " + extraArg)
      else:
        channel = message.split()[-1] # second word (join #channel password)
        self.__bareSay("JOIN " + channel)


  def __quit(self, usr):
    if self._isAdmin(usr):
      self.__bareSay("QUIT :quitting")
      print(("quitting as per " + usr))
      sys.exit()

  
  def respond(self, usr, channel, message):
# this bit is not a command
# TODO (pull this out into a module)
    if any(k in message for k in (".png",".gif",".jpg",".jpeg", ".gifv")) and ("http:" in message or "https:" in message) \
      or ("imgur.com" in message and "gallery" in message) or ("https" in message and "gfycat.com" in message):
     url = re.search("(?P<url>https?://[^\s]+)", message).group("url")
     if url:
       self._insertImg(usr, url, channel)
# this bit is
    if message.startswith(".join"):
      self._join(usr, message)
    if message.strip() == ".quit":
      self.__quit(usr)
    if message.startswith(".imgs"):
      self.ww._generate(self.db.getImgs())
      # hackish TODO
      if os.getenv('USER') == 'pybot':
        self.say(channel, "http://pybot.zero9f9.com/img/")
      else:
        self.say(channel, "http://zero9f9.com/~"+os.getenv('USER')+"/img/") 
    if message.startswith(".onstat"):
      self._onstat(channel)
    if message.startswith(".speak"):
      tmp = message.split(" ",2)
      chnl = tmp[1]
      msg = tmp[2]
      self._speak(usr, chnl, msg)
