from event import Event
import requests

class QDB:
    def __init__(self, events=None, printer_handle=None, bot=None):
        self.events = events
        self.printer = printer_handle
        self.interests = ['__.qdb__'] 
        self.bot = bot
        self.bot.mem_store['qdb'] = {} 

	qdb = Event("__.qdb__")
	qdb.define(msg_definition=".*")
        qdb.subscribe(self)

        #qdb_buff = Event("__qdb_buff__")
        #qdb_buff.define(msg_definition=".*")
        #qdb_buff.subscribe(self)

	self.bot.register_event(qdb, self)
        #self.bot.register_event(qdb_buff, self)

        self.help = ".qdb <search string of first line> | <search string of last line>"
        self.MAX_BUFFER_SIZE = 30

    def add_buffer(self, event=None): 
        """Takes a channel name and line passed to it and stores them in the bot's mem_store dict
        for future access. The dict will have channel as key. The value to that key will be a list
        of dicts associating a username with the message they posted.
        If the buffer size is not yet exceeded, lines are just added. If the buffer
        is maxed out, the oldest line is removed and newest one inserted at the beginning.
        """
        if not event:
            return
        #create a dictionary associating the channel with an empty list if it doesn't exist yet
        if event.channel not in self.bot.mem_store['qdb']:
            self.bot.mem_store['qdb'][event.channel] = []
        try:
        #check for the length of the buffer. if it's too long, pop the last item
            if len(self.bot.mem_store['qdb'][event.channel]) >= self.MAX_BUFFER_SIZE:
                self.bot.mem_store['qdb'][event.channel].pop()
            #define a line as a dict associating user to msg
            #insert the line into the first position in the list
            line = {event.user:event.msg}
            self.bot.mem_store['qdb'][event.channel].insert(0, line)
        except KeyError:
            print "QDB add_buffer() error. Couldn't find dictionary key."
        except IndexError:
            print "QDB add_buffer() error. Couldn't access the list index."

    def format_line(self, line):
        """Takes a dict with a nick:msg relationship and formats it for QDB submission"""
        if len(line) != 1:
            return "\n"
        try:
            return '<' + line.keys()[0].lstrip() + '> ' + line.values()[0] + '\n'
        except KeyError:
            print "QDB format_line() error. Couldn't find dictionary keys."
        except IndexError:
            print "QDB format_line() error. Couldn't get selected index from list."

    def get_qdb_submission(self, channel=None, start_msg='', end_msg=''):
        """Given two strings, start_msg and end_msg, this function will assemble a submission for the QDB.
        start_msg is a substring to search for and identify a starting line. end_msg similarly is used
        to search for the last desired line in the submission. This function returns a string ready
        for submission to the QDB if it finds the desired selection. If not, it returns None.
        """
        if len(start_msg) == 0 or len(end_msg) == 0 or not channel:
            return None
        #search for a matching start string and get the buffer index for the start and end message
        start_index = -1
        end_index = -1
        for index, line in enumerate(self.bot.mem_store['qdb'][channel]):
            if start_msg in line.values()[0]:
                #print 'Start msg: ' + start_msg + ' found at index ' + str(index)
                start_index = index
            if end_msg in line.values()[0]:
                #print 'End msg: ' + end_msg + ' found at index ' + str(index)
                end_index = index
        #check to see if index values are positive. if not, string was not found and we're done
        if start_index == -1 or end_index == -1:
            return None
        #now we generate the string to be returned for submission
        submission = ''
        try:
            for i in reversed(range(end_index, start_index + 1)):
                #print 'Index number is ' + str(i) + ' and current submission is ' + submission
                submission += self.format_line(self.bot.mem_store['qdb'][channel][i])
        except IndexError:
            print "QDB get_qdb_submission() error when accessing list index"
        except KeyError:
            print "QDB get_qdb_submission() error when retrieving dict keys"
        return submission

    def submit(self, qdb_submission):
        """Given a string, qdb_submission, this function will upload the string to hlmtre's qdb
        server. Returns True if successful, returns False if an HTTPError is encountered.
        """
        url = 'http://qdb.zero9f9.com/api.php'
        payload = {'q':'new', 'quote': qdb_submission.rstrip('\n')}
        qdb = requests.post(url, payload)
        try:
            qdb.raise_for_status()
        except requests.exceptions.HTTPError:
            return False
        return True

    def handle(self, event):
        #first we see if we're going to generate a qdb submission, or just add the line to the buffer
        if event.msg.startswith(".qdb "):
            try:
                string_token = event.msg[5:].split('|', 1)
                start_msg = string_token[0].rstrip()
                end_msg = string_token[1].lstrip()
            except IndexError:
                self.printer("PRIVMSG " + event.channel + ' :You must provide two strings to search for separated by a |\n')
                return
            if self.submit(self.get_qdb_submission(event.channel, start_msg, end_msg)):
                self.printer("PRIVMSG " + event.channel + ' :Submission to QDB completed successfully\n')
                self.printer("PRIVMSG " + event.channel + ' :http://qdb.zero9f9.com\n')
            return
        #we only want lines that are PRIVMSGs
        if "PRIVMSG" in event.line:
            self.add_buffer(event)
        #self.printer("PRIVMSG " + event.channel + ' :QDB' + '\n')
