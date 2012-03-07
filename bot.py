#!/usr/bin/env python

import sys
import socket
import string
import os
import datetime
from time import strftime
from collections import defaultdict

CONF=`os.environ['HOME'] + '.pybotrc'`
HOST='localhost'
PORT=6667
NICK='ohai'
IDENT='mypy'
REALNAME='s1ash'
OWNER='hlmtre'
CHANNELINIT='#hhorg'
readbuffer=''

kcount = defaultdict(int)

def parsemsg(line):
	value = 0
	user=line[1:].split('!')
	username=user[0]
	phrase=user[1:]
	p=phrase[-1]
	q=p.split(':')
	p=q[-1]
	c=p[0]
	if c == ">":
		if username not in kcount:
			kcount[username] = 1
		else:
			kcount[username] += 1
		if kcount[username] % 3 == 0:
			value=1
	else: 
		value=0
# end of case/switch


# logging stuff
	logfile=open("./logfile.txt","a")
	date=str(strftime("%Y-%m-%d %H:%M:%S")+'\n')
	logfile.write(date)
	logfile.write("example string\n")#(str(kcount)+'\n')
	logfile.close()
	return (value,username)

# end of parsemsg


# connect to server
s=socket.socket()
s.connect((HOST, PORT))
s.send('NICK '+NICK+'\n')
s.send('USER '+IDENT+ ' 8 ' + ' bla : '+REALNAME+'\n')

# infinite loop to keep parsing lines

while 1:
	line=s.recv(500)
	if line.find('PRIVMSG') != -1:
		print line
		s.send('JOIN '+CHANNELINIT+'\n')
		line=line.rstrip()
		mybool=parsemsg(line)
		code=mybool[0]
		myusername=mybool[1]
		c = int(code)
		if c > 0:
			s.send('PRIVMSG ' + CHANNELINIT + ' ' + myusername + ' :>implying you\'re greentexting' +'\n')
		line=line.split()
		if (line[0] == 'PING'):
			s.send('PONG' + line[1] + '\n')

