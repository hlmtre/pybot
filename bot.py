#!/usr/bin/env python

import sys
import socket
import string
import os
import datetime
from time import strftime
from collections import defaultdict

CONF = `os.environ['HOME'] + '.pybotrc'`
HOST = 'localhost'
PORT = 6667
NICK = 'ohai'
IDENT = 'mypy'
REALNAME = 's1ash'
OWNER = 'hlmtre'
CHANNELINIT = ['#bots', '#hhorg', '#bf3', '#cslug']
readbuffer = ''
DEBUG = False
CONNECTED = False

kcount = defaultdict(int)

## MAIN

if __name__ == "__main__":
	pid = os.fork()
	if pid > 0:
		print "exiting..."
		os._exit(0)
	elif pid == 0:
# we are the child
		print os.getpid()
# connect to server
		s = socket.socket()
		s.connect((HOST, PORT))
		s.send('NICK '+NICK+'\n')
		s.send('USER '+IDENT+ ' 8 ' + ' bla : '+REALNAME+'\n')

# infinite loop to keep parsing lines
		while 1:
			line = s.recv(500)
			if line.find('PRIVMSG') !=  -1:
				if CONNECTED == False:
					for chan in CHANNELINIT:
						s.send('JOIN '+chan+'\n')
						CONNECTED = True
				line_array = line.split()

				ping_response_line = line.split()
				if (ping_response_line[0]  ==  'PING'):
					s.send('PONG ' + ping_response_line[1] + '\n')
					date = str(strftime("%Y-%m-%d %H:%M:%S"))
					print "responding to ping at " + date

				elif "PRIVMSG" in line:
					user_and_mask = line_array[0]
					usr = user_and_mask.split("!", 1)[0]
					usr = usr.split(":", 1)[1]
					channel = line_array[2]
					message = line_array[3]
					message = message.split(":", 1)[1]
					if "ohai" in line and "hello" in line:
						s.send('PRIVMSG ' + channel + ' well hello to you too ' + usr + '\n')
					if message.startswith(">"):
						if usr not in kcount:
							kcount[usr] = 1
						else:
							kcount[usr] += 1
						if kcount[usr] % 3 == 0:
							s.send('PRIVMSG ' + channel + ' ' + usr +': >implying you\'re greentexting\n')

					if DEBUG:
						print user_and_mask + " said to " + channel + " \"" + msg + "\""
						print kcount
