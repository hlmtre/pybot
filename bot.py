#!/usr/bin/env python

import sys
import socket
import string
import os
import datetime
from time import strftime
from collections import defaultdict
from multiprocessing import Process

DEBUG = False
kcount = defaultdict(int)

CONF = './.pybotrc'
if os.environ.has_key('HOME'):
	CONF = `os.environ['HOME'] + '.pybotrc'`


def implying(s, usr):
	global kcount
	if usr not in kcount:
		kcount[usr] = 1
	else:
		kcount[usr] += 1
	if kcount[usr] % 3 == 0:
		s.send('PRIVMSG ' + channel + ' ' + usr +': >implying you\'re greentexting\n')

def pong(s):
	s.send('PONG ' + ping_response_line[1] + '\n')
	date = str(strftime("%Y-%m-%d %H:%M:%S"))
	print "responding to ping at " + date
		
def worker():

	HOST = 'localhost'
	PORT = 6667
	NICK = 'ohai'
	IDENT = 'mypy'
	REALNAME = 's1ash'
	OWNER = 'hlmtre'
	CHANNELINIT = ['#bots', '#hhorg', '#bf3', '#cslug']
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
		line = s.recv(500)
		print line
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
					user_and_mask = line_array[0]
					usr = user_and_mask.split("!", 1)[0].split(":", 1)[1]
					channel = line_array[2]
					message = line_array[3].split(":", 1)[1]
					if "ohai" in line and "hello" in line:
						s.send('PRIVMSG ' + channel + ' well hello to you too ' + usr + '\n')
					if message.startswith(">"):
						implying(s, usr)

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