#!/usr/bin/env python
#
# v0.2
# TODO: add threading support, one for each network
#
#
#


import sys
import socket
import string
import os
import datetime
import time
import select
import traceback
import threading

from multiprocessing import Process
import botbrain
import logger
import db
import confman


class Bot(threading.Thread):
	def __init__(self, conf, network):
		threading.Thread.__init__(self)
		global DEBUG
		self.brain = None
		self.network = network
		DEBUG = True
		self.OFFLINE = False
#CHANNELINIT = ['#bots']
#CHANNELINIT = ['#bots', '#bf3', '#hhorg', '#dayz', '#cslug']
		self.CONNECTED = False
		self.conf = conf

		self.CHANNELINIT = conf.getChannels()
		#self.network = conf.getNetwork()
# this will be the socket
		self.s = None # each bot holds its own socket open to the network
		self.brain = botbrain.BotBrain(self.send) # if this is unclear: send is a function pointer, to allow the botbrain to send
# TODO FIXME figure out how to scope <blank>.send and <blank>.worker (below, in run()) 

		
	def send(self, message):
		if OFFLINE:
			print message
		else:
			self.s.send(message)
			
		
	def pong(self, response):
		send('PONG ' + response + '\n')
		#date = str(time.strftime("%Y-%m-%d %H:%M:%S"))
		#l = logger.Logger()
		#l.write("responding to PING at " + date + '\n')
			

	def processline(self, line):
		global CONNECTED
		
		if DEBUG:
			print line
		
		try:
			if line.startswith("PING"):
				ping_response_line = line.split(":", 1)
				pong(ping_response_line[1])

# current hackish solution for seen
# this is SO INCREDIBLY WRONG AND GROSS
			else:
# let's update the database because the events besides PRIVMSG never get past here
				if line.split()[1] == "JOIN" or line.split()[1] ==  "QUIT" or line.split()[1] == "PART":
			#		print line
					if "PART" in line:
						word = "PART"
# strip username out of line, lstrip for stripping out :
						self.brain._updateSeen(line.split("!",1)[0].lstrip(":"), line.rsplit(":",1)[-1], word)
					elif "JOIN" in line:
						word = "JOIN"
						self.brain._updateSeen(line.split("!",1)[0].lstrip(":"), "immmmmma joinin", word)
					else:
						word = "QUIT"
						self.brain._updateSeen(line.split("!",1)[0].lstrip(":"), line.rsplit(":",1)[-1], word)
				if self.CONNECTED == False:
					time.sleep(1)
					for chan in self.CHANNELINIT:
						send('JOIN '+chan+'\n')
						if DEBUG:
							print "#### JOINING " + chan + " ####"
					self.CONNECTED = True
				
				line_array = line.split()
				user_and_mask = line_array[0][1:]
				usr = user_and_mask.split("!")[0]
				channel = line_array[2]
				try: 
					message = line.split(":",2)[2]
					self.brain.respond(usr, channel, message)
				except IndexError:
					print "index out of range.", line
				
				#p = Process(target=botbrain.respond, args=(s, usr, channel, message))
				#p.start()
				
		except Exception:
			print "Unexpected error:", sys.exc_info()[0]
			traceback.print_exc(file=sys.stdout)
			
	def worker(self):
		if self.network is None:
			self.network = 'zero9f9.com'
		try:
			if "minus22" in socket.gethostname() or "barge" in socket.gethostname():
				self.HOST = self.network
				self.NICK = 'ohai'
			else:
				self.HOST = self.network
				self.NICK = 'localohai'
		except:
			self.HOST = self.network
			self.NICK = 'localohai'

		# we have to cast it to an int, otherwise the connection fails silently and the entire process dies
		#PORT = int(cm.getPort())
		self.PORT = int(self.conf.getPort())
		self.IDENT = 'mypy'
		self.REALNAME = 's1ash'
		self.OWNER = self.conf.getOwner() 
		
		print os.getpid()
		# connect to server
		self.s = socket.socket()
		try:
			self.s.connect((self.HOST, self.PORT)) # force them into one argument
		except Exception, e:
			print Exception, e
		try:
			self.s.send('NICK '+self.NICK+'\n')
			self.s.send('USER '+self.IDENT+ ' 8 ' + ' bla : '+self.REALNAME+'\n') # yeah, don't delete this line
			time.sleep(3) # allow services to catch up
			self.s.send('PRIVMSG nickserv identify '+self.conf.getIRCPass()+'\n')  # we're registered!
		except Exception, e:
			print Exception, e

		self.s.setblocking(1)
		
		read = ""
		
		# infinite loop to keep parsing lines
		while 1:
			time.sleep(1)
			ready = select.select([self.s],[],[], 1)
			if ready[0]:
				read = read + self.s.recv(1024)
				lines = read.split('\n')
				
				# Important: all lines from irc are terminated with '\n'. lines.pop() will get you any "to be continued"
				# line that couldn't fit in the socket buffer. It is stored and tacked on to the start of the next recv.
				read = lines.pop() 
				for line in lines:
					line = line.rstrip()
					self.processline(line)			

	def run(self):
		bot.Bot.worker(self)
# end class Bot
							
## MAIN ## ACTUAL EXECUTION STARTS HERE

if __name__ == "__main__":
	import bot
	if len(sys.argv) > 1:
		CONF = sys.argv[1]
	else: CONF = "~/.pybotrc"

	cm = confman.ConfManager(CONF)
	net_list = cm.getNetworks()
	i = 0
	if cm.getNumNets() > 1:
		for c in cm.getNetworks():
			b = bot.Bot(cm, net_list[i])
			b.start()
			i += 1
	else:
		b = bot.Bot(cm, net_list)
		b.start()
	#if DEBUG:
	#	worker() # run in foreground for debugging
	#
	#else:
	
	if os.name == "posix":
		pid = os.fork()
		if pid == 0:
			worker()
		elif pid > 0:
			print "forking to background..."
			sys.exit(0)

	else: # since we don't have fork on windows
		p = Process(target=worker)
		p.start()
		print os.getpid()
