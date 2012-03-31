#!/usr/bin/env python

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

DEBUG = False
OFFLINE = False
CHANNELINIT = ['#bots', '#bf3']
CONNECTED = False

CONF = './.pybotrc'
if os.environ.has_key('HOME'):
	CONF = `os.environ['HOME'] + '.pybotrc'`

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
	date = str(time.strftime("%Y-%m-%d %H:%M:%S"))
		

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

		elif "PRIVMSG" in line:
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
			message = line.split(":",2)[2]
			
			#p = Process(target=botbrain.respond, args=(s, usr, channel, message))
			#p.start()
			brain.respond(usr, channel, message)
			
	except Exception:
		print "Unexpected error:", sys.exc_info()[0]
		traceback.print_exc(file=sys.stdout)
		
def worker():

	HOST = 'zero9f9.com'
	PORT = 6667
	NICK = 'ohai'
	IDENT = 'mypy'
	REALNAME = 's1ash'
	OWNER = 'hlmtre'
	
	print os.getpid()
	# connect to server
	global s
	s = socket.socket()
	s.connect((HOST, PORT))
	s.send('NICK '+NICK+'\n')
	s.send('USER '+IDENT+ ' 8 ' + ' bla : '+REALNAME+'\n')
	s.setblocking(0)
	
	# infinite loop to keep parsing lines
	while 1:
		ready = select.select([s],[],[], 1)
		if ready[0]:
			line = s.recv(4096)
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
