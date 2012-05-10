import ascii
from collections import defaultdict
import bf3api
import time
import logger 
import datetime
import battlelog
import urllib2
import urlparse
import re
from xml.dom.minidom import parseString

api = bf3api.API(None, '360')

bf3players = {'tarehart': ('tarehart', '360'),
							#'hlmtre': ('hellmitre', '360'),
							'willfro': ('fro4thought', '360'),
							'BoneKin': ('BoneKin', '360'),
							'Lucifer7': ('Lucifer7', '360'),
							'i7': ('Infinite Se7en', '360')}

def getbf3stats(message):
#	global bf3players
	global api
#		for k,v in bf3players.iteritems():
#			if k in message:
#				data = api.player(v[0], v[1], "clear,ranking")
#				return formatbf3data(k, data)

	gt = message.split(None, 2)[2].strip() # grab gamertag off the end and strip it of terminators
	command = message.split(None, 2)[1].strip()

	data = api.player(gt, '360', "clear,ranking")

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
		self.kcount = defaultdict(int)
		self.starttime = time.time()
		self.localtime = time.localtime()
		
		self.microphone = microphone

	def say(self, channel, thing):
		self.microphone('PRIVMSG ' + channel + ' :' + str(thing) + '\n')

	def _getyoutubetitle(self, line, channel):
		url = re.search("youtube.com[\S]+", line).group(0)
		if url:
			video_tag = urlparse.urlparse(url).query.split("=")[1].split("&")[0]
			if video_tag.__len__() > 1:
				response = urllib2.urlopen("https://gdata.youtube.com/feeds/api/videos/"+video_tag+"?v=2").read()
				xml_response = parseString(response)
				titletag = xml_response.getElementsByTagName('title')[0]
				video_title = titletag.childNodes[0].nodeValue
				self.say(channel, "YouTube: "+video_title)



	def _uptime(self, channel):
		self.say(channel,"I've been up " +str(datetime.timedelta(seconds=time.time() - self.starttime))[:7] + ", since "+time.strftime("%a, %d %b %Y %H:%M:%S -0800", self.localtime))

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
		if "ohai" in message and "hello" in message:
			self.say(channel, 'well hello to you too ' + usr)
		if "youtube.com" in message:
			self._getyoutubetitle(message, channel)
		if message.startswith(">"):
			self.implying(channel, usr)
		#if message.startswith("paint "):
		#	self.paint(channel, message.split()[1])
		if message.startswith(".rainbow"):
			self.say(channel, ascii.rainbow())
		#if "bf3" in message and "stats" in message:
		if message.startswith(".help"):
			self._help(usr)			
		if message.startswith(".bf3"):
			stats = getbf3stats(message)
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
