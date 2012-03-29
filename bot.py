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
CHANNELINIT = ['#hhorg', '#bf3', '#bots']
readbuffer = ''
DEBUG = False

kcount = defaultdict(int)

def parsemsg(line):
	value = 0

	# grab first occurrence of !
	# fixes array index error on lines which contained more than one !
	user = line[1:].split('!', 1)
	username = user[0]
	phrase = user[1:]
	p = phrase[-1]
# same deal here
	q = p.split(':', 1)
#	print q
	p = q[-1]
	c = p[0]
	if c  ==  ">":
		if username not in kcount:
			kcount[username] = 1
		else:
			kcount[username] +=  1
		if kcount[username] % 3  ==  0:
			value = 1
	else: 
		value = 0
# end of case/switch


# logging stuff
	logfile = open("./logfile.txt","a")
	date = str(strftime("%Y-%m-%d %H:%M:%S"))
	logfile.write("at " + date + ": ")
	logfile.write(username + " greentexted.\n")#(str(kcount)+'\n')
	logfile.write(username + " has greentexted " + str(kcount[username]) + " times since i've been running\n")
	logfile.close()
	return (value,username)

# end of parsemsg

## MAIN

if __name__ == "__main__":
# connect to server
	s = socket.socket()
	s.connect((HOST, PORT))
	s.send('NICK '+NICK+'\n')
	s.send('USER '+IDENT+ ' 8 ' + ' bla : '+REALNAME+'\n')

	for chan in CHANNELINIT:
		child_pid = os.fork()
		print str(child_pid)
		if child_pid == 0:
			print str(child_pid)
# infinite loop to keep parsing lines
			while 1:
				line = s.recv(500)
				line_array = line.split()

				ping_response_line = line.split()
				if (ping_response_line[0]  ==  'PING'):
					s.send('PONG ' + ping_response_line[1] + '\n')
					date = str(strftime("%Y-%m-%d %H:%M:%S"))
					print "responding to ping at " + date

				elif "PRIVMSG" in line:
					user_and_mask = line_array[0]
					usr = user_and_mask.split("!", 1)[0]
					channel = line_array[2]
					message = line_array[3]
					if "ohai" in line and "hello" in line:
						s.send('PRIVMSG ' + chan + ' well hello to you too ' + usr + '\n')

#	print line
				if line.find('PRIVMSG') !=  -1:
					s.send('JOIN '+chan+'\n')
					line = line.rstrip()
# grab message to channel
					msg = line.split(":", 2)[2]
					mybool = parsemsg(line)
					code = mybool[0]
					myusername = mybool[1]
					if DEBUG:
						print user_and_mask + " said to " + channel + " " + msg
					c = int(code)
					if c > 0:
						s.send('PRIVMSG ' + chan + ' ' + myusername + ': :>implying you\'re greentexting' +'\n')
