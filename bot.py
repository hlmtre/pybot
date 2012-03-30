#!/usr/bin/env python

import sys
import socket
import string
import os
import datetime
import time

from multiprocessing import Process
import botbrain

DEBUG = False


CONF = './.pybotrc'
if os.environ.has_key('HOME'):
	CONF = `os.environ['HOME'] + '.pybotrc'`


		
		
def worker():

	HOST = 'zero9f9.com'
	PORT = 6667
	NICK = 'tarehai'
	IDENT = 'mypy'
	REALNAME = 's1ash'
	OWNER = 'hlmtre'
	CHANNELINIT = ['#bots', '#hhorg']
	readbuffer = ''
	CONNECTED = False

	print os.getpid()
	# connect to server
	s = socket.socket()
	s.connect((HOST, PORT))
	s.send('NICK '+NICK+'\n')
	s.send('USER '+IDENT+ ' 8 ' + ' bla : '+REALNAME+'\n')

	# infinite loop to keep parsing lines
	while 1:
		time.sleep(.01)
		line = s.recv(500)
		if line.find('PRIVMSG') !=  -1:
			try:
				if CONNECTED == False:
					for chan in CHANNELINIT:
						s.send('JOIN '+chan+'\n')
						CONNECTED = True
				line_array = line.split()
				ping_response_line = line.split()
				if (ping_response_line[0]  ==  'PING'):
					pong(s)

				elif "PRIVMSG" in line:
					user_and_mask = line_array[0][1:]
					usr = user_and_mask.split("!")[0]
					channel = line_array[2]
					message = line.split(":",2)[2]
		
					botbrain.respond(s, usr, channel, message)
					
					if DEBUG:
						print user_and_mask + " said to " + channel + " \"" + msg + "\""
						print kcount
			except Exception:
				print "Unexpected error:", sys.exc_info()[0]
						
						
## MAIN

if __name__ == "__main__":
	print os.getpid()
	p = Process(target=worker)
	p.start()