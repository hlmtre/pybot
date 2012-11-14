import ascii
from collections import defaultdict
import bf3api
import time
import logger 
import datetime
import battlelog
import urllib2
import json
import urlparse
import re
from xml.dom.minidom import parseString
import db
from datetime import datetime

api = bf3api.API(None, '360')
yth = dict()
db = db.DB()

chanlist = []
namelist = []

bf3players = {'tarehart': ('tarehart', '360'),
							#'hlmtre': ('hellmitre', '360'),
							'willfro': ('fro4thought', '360'),
							'BoneKin': ('BoneKin', '360'),
							'Lucifer7': ('Lucifer7', '360'),
							'i7': ('Infinite Se7en', '360')}

def getbf3stats(message, platform):
#	global bf3players
	global api
#		for k,v in bf3players.iteritems():
#			if k in message:
#				data = api.player(v[0], v[1], "clear,ranking")
#				return formatbf3data(k, data)

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
	
	def __init__(self, microphone):							
#  store kcount of >implying
		self.kcount = defaultdict(int)
# get time for uptime start
		self.starttime = time.time()
# get time for current length of uptime
		self.localtime = time.localtime()
		
# get handle on output
		self.microphone = microphone

	def _seen(self, user, channel):
		answer = db.getSeen(user)
		if answer != "None" and answer != "" and answer != None:
			if answer[3] ==  "JOIN":
				word = "joining"
			elif answer[3] == "PART":
				word = "parting"
			else:
				word = "quitting"
			self.say(channel, user + " was last seen " + word + " channel saying \"" + answer[2] + "\" " + self.__prettyDate(answer[1]))
		else:
			self.say(channel, user + " not seen exiting.")

	def _updateSeen(self, user, statement, event):
		db.updateSeen(user, statement, event)
#	def _initSeen(self, chanlist):
#		self.chanlist = chanlist
#		for chan in self.chanlist:
#			self.__bareSay('NAMES ' + chan + '\n')

	def __bareSay(self, thing):
		self.microphone(thing + '\n')

	def say(self, channel, thing):
		self.microphone('PRIVMSG ' + channel + ' :' + str(thing) + '\n')

	def _weather(self, channel, zipcode):
		url = 'http://api.wunderground.com/api/1fe31b3b4cfdab66/conditions/lang:EN/q/'+zipcode+'.json'
		response = urllib2.urlopen(url)
		json_string = response.read()
		parsed_json = json.loads(json_string)
		self.say(channel, parsed_json['current_observation']['display_location']['city'] + ", " + parsed_json['current_observation']['display_location']['state'] + ": " + parsed_json['current_observation']['feelslike_string'])

	def _getyoutubetitle(self, line, channel):
		url = re.search("youtube.com[\S]+", line).group(0)
		if url:
			video_tag = urlparse.urlparse(url).query.split("=")[1].split("&")[0]
			if video_tag.__len__() > 1:
				response = urllib2.urlopen("https://gdata.youtube.com/feeds/api/videos/"+video_tag+"?v=2").read()
				xml_response = parseString(response)
				duration = xml_response.getElementsByTagName('yt:duration')
				ulength = duration[0].getAttribute("seconds")
				alength = ulength.encode('ascii', 'ignore')
				length = str(datetime.timedelta(seconds=int(alength)))
				titletag = xml_response.getElementsByTagName('title')[0]
				video_title = titletag.childNodes[0].nodeValue
				self.say(channel, "YouTube: "+video_title + " ("+length+")")
				yth[video_title] = line


	def _ctof(self, channel, c_temp):
		c = float(c_temp)
		f = (c * 1.8)+32
		self.say(channel, str(f) + "* F")

	def _ftoc(self, channel, f_temp):
		f = float(f_temp)
		c = (f - 32)*(.5555)
		self.say(channel, str(c) + "* C")

	def _ythistory(self, channel):
		global yth
		i = 0 
		for entry in reversed(yth):
			i+=1
			if i > 5:
				break
			else:
				self.say(channel,yth[entry] + " - " + entry)
				if len(yth) > 10:
					yth.clear()

	def _uptime(self, channel):
		self.say(channel,"I've been up " +str(datetime.timedelta(seconds=time.time() - self.starttime))[:7] + ", since "+time.strftime("%a, %d %b %Y %H:%M:%S -0800", self.localtime))

	def _speak(self, user, target, message):
		if user == "hlmtre":
			if target.startswith("#"):
				self.say(target, message)	
			else:
				target = "#" + target
				self.say(target, message)

	def _onstat(self, channel):
		self.say(channel, "Yep, I'm on. Idiot.")

	def _help(self, user):
		self.microphone('PRIVMSG ' + user + ' :' + "COMMANDS:\n")
		self.microphone('PRIVMSG ' + user + ' :' + ".bf3 [spm, kdr, wlr, stats],\n")
		self.microphone('PRIVMSG ' + user + ' :' + ".rainbow,\n")
		self.microphone('PRIVMSG ' + user + ' :' + ".uptime,\n")
		self.microphone('PRIVMSG ' + user + ' :' + "and this help message.\n")
		self.microphone('PRIVMSG ' + user + ' :' + "More functionality to be added.\n")

	
	def respond(self, usr, channel, message):
		if message.startswith(".seen"):
			self._seen(message.split()[-1], channel)
		if message.startswith(".weather"):
			_z = message.split()
			if _z[-1] != "":
				self._weather(channel, _z[-1])
		if message.startswith(".ctof"):
			last = message.split()
			if last[-1] != "":
				self._ctof(channel, last[-1])
		if message.startswith(".ftoc"):
			last = message.split()
			if last[-1] != "":
				self._ftoc(channel, last[-1]) 
		if "ohai" in message and "hello" in message:
			self.say(channel, 'well hello to you too ' + usr)
		if "youtube.com" in message:
			self._getyoutubetitle(message, channel)
		#if message.startswith(">"):
			#self.implying(channel, usr)
		#if message.startswith("paint "):
		#	self.paint(channel, message.split()[1])
		if message.startswith(".yth"):
			self._ythistory(channel)
		if message.startswith(".rainbow"):
			self.say(channel, ascii.rainbow())
		#if "bf3" in message and "stats" in message:
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
		
	def paint(self, channel, url):
		arr = ascii.asciify(url)
		for line in arr:
			self.say(channel, line)

	def implying(self, channel, usr):
		kcount = self.kcount
		if usr not in kcount:
			kcount[usr] = 1
		else:
			kcount[usr] += 1
		if kcount[usr] % 3 == 0:
			self.say(channel, " " + usr + " >implying you're greentexting")
			date = str(time.strftime("%Y-%m-%d %H:%M:%S"))
			l = logger.Logger()
			l.write("user " + usr + " implying at " + date)

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
