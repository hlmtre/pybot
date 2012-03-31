import ascii
from collections import defaultdict
import bf3api

api = bf3api.API()

bf3players = {'tarehart': ('tarehart', '360'),
							'hlmtre': ('hellmitre', '360'),
							'willfro': ('fro4thought', '360'),
							'BoneKin': ('BoneKin', '360'),
							'Lucifer7': ('Lucifer7', '360'),
							'i7': ('Infinite Se7en', '360')}

def getbf3stats(message):
		global bf3players
		global api
		for k,v in bf3players.iteritems():
			if k in message:
				print "message in bf3stats is: " + message
				data = api.player(v[0], v[1], "clear,ranking")
				return formatbf3data(k, data)
			else:
				gt = message.split(None, 2)[2] # grab gamertag off the end
				print gt
				
def formatbf3data(player, data):
	return [player + "'s SPM: " + str(data.Stats.Ranking.Spm.v)[:6]]
	

class BotBrain:
	BRAINDEBUG = False
	
	def __init__(self, microphone):							
		self.kcount = defaultdict(int)
		
		self.microphone = microphone

	def say(self, channel, thing):
		self.microphone('PRIVMSG ' + channel + ' :' + str(thing) + '\n')

	
	def respond(self, usr, channel, message):
		if "ohai" in message and "hello" in message:
			self.say(channel, 'well hello to you too ' + usr)
		if message.startswith(">"):
			implying(usr)
		if message.startswith("paint "):
			self.paint(channel, message.split()[1])
		if "rainbow" in message:
			self.say(channel, ascii.rainbow())
		#if "bf3" in message and "stats" in message:
		if message.startswith(".bf3") and "stats" in message:
			stats = getbf3stats(message)
			for line in stats:
				self.say(channel, line)
			
		
	def paint(self, channel, url):
		arr = ascii.asciify(url)
		for line in arr:
			self.say(channel, line)

	def implying(self, usr):
		kcount = self.kcount
		if usr not in kcount:
			kcount[usr] = 1
		else:
			kcount[usr] += 1
		if kcount[usr] % 3 == 0:
			self.say(channel, usr + ">implying you're greentexting")

