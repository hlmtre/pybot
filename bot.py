#!/usr/bin/env python

# test
import sys
import socket
import string
import os
import datetime
import time
import select
import traceback

from multiprocessing import Process
import botbrain
import logger
import db
import confman

# suppress warnings
sys.stderr = open("/dev/null","w")


DEBUG = False
OFFLINE = False
CHANNELINIT = ['#bots']
#CHANNELINIT = ['#bots', '#bf3', '#hhorg', '#dayz', '#cslug']
CONNECTED = False

if len(sys.argv) > 1:
	CONF = sys.argv[1]
else:
	if os.environ.has_key('HOME'):
		CONF = os.environ['HOME'] + '/.pybotrc'

cm = confman.ConfManager(CONF)

CHANNELINIT = cm.getChannels()
network = cm.getNetwork()


# this will be the socket
s = None

	
def send(message):
	if OFFLINE:
		print message
	else:
		s.send(message)
		
brain = botbrain.BotBrain(send)
	
def pong(response):
	send('PONG ' + response + '\n')
	#date = str(time.strftime("%Y-%m-%d %H:%M:%S"))
	#l = logger.Logger()
	#l.write("responding to PING at " + date + '\n')
		

def processline(line):
	global CONNECTED
	global CHANNELINIT
	global brain
	
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
					brain._updateSeen(line.split("!",1)[0].lstrip(":"), line.rsplit(":",1)[-1], word)
				elif "JOIN" in line:
					word = "JOIN"
					brain._updateSeen(line.split("!",1)[0].lstrip(":"), "immmmmma joinin", word)
				else:
					word = "QUIT"
					brain._updateSeen(line.split("!",1)[0].lstrip(":"), line.rsplit(":",1)[-1], word)
			if CONNECTED == False:
				for chan in CHANNELINIT:
					send('JOIN '+chan+'\n')
					if DEBUG:
						print "#### JOINING " + chan + " ####"
				CONNECTED = True
			
			line_array = line.split()
			user_and_mask = line_array[0][1:]
			usr = user_and_mask.split("!")[0]
			channel = line_array[2]
			try: 
				message = line.split(":",2)[2]
				brain.respond(usr, channel, message)
			except IndexError:
				print "index out of range."
				print line
			
			#p = Process(target=botbrain.respond, args=(s, usr, channel, message))
			#p.start()
			
	except Exception:
		print "Unexpected error:", sys.exc_info()[0]
		traceback.print_exc(file=sys.stdout)
		
def worker():
	global network
	if network is not None and len(network) > 1:
		network = network
	else:
		network = 'zero9f9.com'
	try:
		if "minus22" in socket.gethostname() or "barge" in socket.gethostname():
			HOST = 'localhost'
			NICK = 'ohai'
		else:
			HOST = network
			NICK = 'localohai'
	except:
		HOST = network
		NICK = 'localohai'

	PORT = 6667
	IDENT = 'mypy'
	REALNAME = 's1ash'
	OWNER = cm.getOwner() 
	
	print os.getpid()
	# connect to server
	global s
	s = socket.socket()
	try:
		s.connect((HOST, PORT))
	except Exception, e:
		alert('something\'s wrong with %s:%d. Exception type is %s' % (address, port, `e`))
		sys.exit(3)

	try:
		s.send('NICK '+NICK+'\n')
		s.send('USER '+IDENT+ ' 8 ' + ' bla : '+REALNAME+'\n')
	except Exception, e:
		alert('something\'s wrong with %s:%d. Exception type is %s' % (address, port, `e`))
		sys.exit(4)
	s.setblocking(1)
	
	read = ""
	
	# infinite loop to keep parsing lines
	while 1:
		time.sleep(1)
		ready = select.select([s],[],[], 1)
		if ready[0]:
			read = read + s.recv(1024)
			lines = read.split('\n')
			
			# Important: all lines from irc are terminated with '\n'. lines.pop() will get you any "to be continued"
			# line that couldn't fit in the socket buffer. It is stored and tacked on to the start of the next recv.
			read = lines.pop() 
			for line in lines:
				line = line.rstrip()
				processline(line)			
						
## MAIN

if __name__ == "__main__":
	if os.name == "posix":
		pid = os.fork()
		if pid == 0:
			worker()
		elif pid > 0:
			print "forking to background..."
			os._exit(0)

	else: # since we don't have fork on windows
		p = Process(target=worker)
		p.start()
		print os.getpid()
