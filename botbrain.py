from collections import defaultdict
import webwriter
import bf3api
import time
import logger 
import datetime
import battlelog
import urllib2
import json
from urlparse import urlparse, parse_qsl
import re
from xml.dom.minidom import parseString
import db
from datetime import datetime, timedelta
import sys
import os

api = bf3api.API(None, '360')

bf3players = {'tarehart': ('tarehart', '360'),
              #'hlmtre': ('hellmitre', '360'),
              'willfro': ('fro4thought', '360'),
              'BoneKin': ('BoneKin', '360'),
              'Lucifer7': ('Lucifer7', '360'),
              'i7': ('Infinite Se7en', '360')}

def getbf3stats(message, platform):
# global bf3players
  global api

  gt = message.split(None, 2)[2].strip() # grab gamertag off the end and strip it of terminators
  command = message.split(None, 2)[1].strip()

  data = api.player(gt, platform, "clear,ranking")

  l = logger.Logger()
  date = str(time.strftime("%Y-%m-%d %H:%M:%S"))
  string = "getting " + command + " for player " + gt + " at " + date + '\n'
  l.write(string)

  return formatbf3data(gt, command, data)
    
def formatbf3data(player, command, data):
  if data.status == "data":
    if command == "spm":
      return [player + "'s SPM: " + str(data.Stats.Ranking.Spm.v)[:6]]
    elif command == "kdr":
      return [player + "'s KDR: " + str(data.Stats.Ranking.Kdr.v)[:6]]
    elif command == "wlr":
      return [player + "'s WLR: " + str(data.Stats.Ranking.Wlr.v)[:6]]
    elif command == "stats":
      l = [player+"'s stats: ", "KDR: "+str(data.Stats.Ranking.Kdr.v)[:6], "SPM: "+str(data.Stats.Ranking.Spm.v)[:6], "Headshots/kill: "+str(data.Stats.Ranking.Hskillperc.v)[:6], "win/loss: "+str(data.Stats.Ranking.Wlr.v)[:6]]
      return l
      
  elif data.status == "notfound":
    return [player + " not found "]
  else:
    return ["ERROR"]
  

def getbf3last(message):
  global api
  
  command = message.split(None, 2)[1].strip()
  gt = message.split(None, 2)[2].strip() # grab gamertag off the end and strip it of terminators
  fact = battlelog.getLatestGameFact(api, gt, command)
  return gt + "'s latest " + command + " is " + str(fact)[:6]

  
  
class BotBrain:
  BRAINDEBUG = False
  
  def __init__(self, microphone, bot=None):             
# get time for uptime start
    self.starttime = time.time()
# get time for current length of uptime
    self.localtime = time.localtime()
# get handle on output

    self.microphone = microphone
    self.bot = bot
    yth = dict()
    self.db = db.DB(self.bot)
    self.ww = webwriter.WebWriter()

  def _isAdmin(self, username):
    if self.bot.conf.getOwner(self.bot.network) == username:
      return True
    if self.db._isAdmin(username):
      return True
    return False

  def getMicrophone(self):
    return self.microphone

  def _updateSeen(self, user, statement, event):
    self.db.updateSeen(user, statement, event)
  
  def _insertImg(self, user, url, channel):
    self.db._insertImg(user, url, channel)

  def __bareSay(self, thing):
    self.microphone(thing + '\n')

  def say(self, channel, thing):
    self.microphone('PRIVMSG ' + channel + ' :' + str(thing) + '\n')

  def notice(self, channel, thing):
    self.microphone('NOTICE ' + channel + ' :' + str(thing) + '\n')

  # now implemented as a module
  #def _weather(self, channel, zipcode):

  # now implemented as a module
 # def _getyoutubetitle(self, line, channel):

  def _ctof(self, channel, c_temp):
    c = float(c_temp)
    f = (c * 1.8)+32
    self.say(channel, str(f) + "* F")

  def _ftoc(self, channel, f_temp):
    f = float(f_temp)
    c = (f - 32)*(.5555)
    self.say(channel, str(c) + "* C")

  def _uptime(self, channel):
    self.say(channel,"I've been up " +str(timedelta(seconds=time.time() - self.starttime))[:7] + ", since "+time.strftime("%a, %d %b %Y %H:%M:%S -0800", self.localtime))

  def _speak(self, user, target, message):
    if target.startswith("#"):
      self.say(target, message) 
    else:
      target = "#" + target
      self.say(target, message)

  def _onstat(self, channel):
    self.say(channel, "Yep, I'm on. Idiot.")

  def _help(self, user):
    self.microphone('PRIVMSG ' + user + ' :' + ".bf3 [spm, kdr, wlr, stats],\n")
    self.microphone('PRIVMSG ' + user + ' :' + ".uptime,\n")
    self.microphone('PRIVMSG ' + user + ' :' + ".imgs,\n")
    self.microphone('PRIVMSG ' + user + ' :' + ".ctof [celsius],\n")
    self.microphone('PRIVMSG ' + user + ' :' + ".ftoc [fahrenheit],\n")

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
      print "quitting as per " + usr
      sys.exit()

  
  def respond(self, usr, channel, message):
# this bit is not a command
    if (".png" in message or ".gif" in message or ".jpg" in message or ".jpeg" in message) and ("http:" in message) or ("imgur.com" in message and "gallery" in message):
     url = re.search("(?P<url>https?://[^\s]+)", message).group("url")
     if url:
       self._insertImg(usr, url, channel)
# this bit is
    if message.startswith("join"):
      self._join(usr, message)
    if message.startswith("quit"):
      self.__quit(usr)
    if message.startswith(".imgs"):
      self.ww._generate(self.db._getImgs())
      # hackish TODO
      if os.getenv('USER') == 'pybot':
        self.say(channel, "http://pybot.zero9f9.com/img/")
      else:
        self.say(channel, "http://zero9f9.com/~"+os.getenv('USER')+"/img/")
    if message.startswith(".seen"):
      self._seen(message.split()[-1], channel)
    if message.startswith(".ctof"):
      last = message.split()
      if last[-1] != "":
        self._ctof(channel, last[-1])
    if message.startswith(".ftoc"):
      last = message.split()
      if last[-1] != "":
        self._ftoc(channel, last[-1]) 
    if message.startswith(".help"):
      self._help(usr)     
    if message.startswith(".bf3pc"):
      stats = getbf3stats(message, 'pc')
      try:
        for line in stats:
          self.say(channel, line)
      except TypeError:
        self.say(channel, "WOOPS")
    elif message.startswith(".bf3"):
      stats = getbf3stats(message, '360')
      try:
        for line in stats:
          self.say(channel, line)
      except TypeError:
        self.say(channel, "WOOPS")
    if message.startswith(".lastbf3"):
      last = getbf3last(message)
      self.say(channel, last)
    if message.startswith(".uptime"):
      self._uptime(channel)
    if message.startswith(".onstat"):
      self._onstat(channel)
    if message.startswith(".speak"):
      tmp = message.split(" ",2)
      chnl = tmp[1]
      msg = tmp[2]
      self._speak(usr, chnl, msg)

# utility function
  def __prettyDate(self,time):
    now = datetime.now()
    if type(time) is int:
      diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
      diff = now - time 
    elif not time:
      diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
      return ''

    if day_diff == 0:
      if second_diff < 10:
        return "just now"
      if second_diff < 60:
        return str(second_diff) + " seconds ago"
      if second_diff < 120:
        return  "a minute ago"
      if second_diff < 3600:
        return str( second_diff / 60 ) + " minutes ago"
      if second_diff < 7200:
        return "an hour ago"
      if second_diff < 86400:
        return str( second_diff / 3600 ) + " hours ago"
      if day_diff == 1:
        return "Yesterday"
      if day_diff < 7:
        return str(day_diff) + " days ago"
      if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
      if day_diff < 365:
        return str(day_diff/30) + " months ago"
      return str(day_diff/365) + " years ago"
