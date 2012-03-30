import ascii
from collections import defaultdict

BRAINDEBUG = False

kcount = defaultdict(int)

def say(s, channel, thing):
	if BRAINDEBUG:
		print str(thing)
	else:
		s.send('PRIVMSG ' + channel + ' :' + str(thing) + '\n')

	
def respond(s, usr, channel, message):
	if "ohai" in message and "hello" in message:
		say(s, channel, 'well hello to you too ' + usr)
	if message.startswith(">"):
		implying(s, usr)
	if message.startswith("paint "):
		paint(s, channel, message.split()[1])
	if "rainbow" in message:
		say(s, channel, ascii.rainbow())
	

def paint(s, channel, url):
	arr = ascii.asciify(url)
	for line in arr:
		say(s, channel, line)

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