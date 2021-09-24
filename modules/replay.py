# NEEDS
# adding a bold character for '<user> MEANT so say'

from event import Event


class Replay:
    def __init__(self, events=None, printer_handle=None, bot=None, say=None):
        self.events = events
        self.printer = printer_handle
        self.interests = ['__.replay__']
        self.bot = bot
        self.say = say

        self.bot.mem_store['replace'] = {}
        # define a key for _recent since that will not be a potential channel
        # name
        self.bot.mem_store['replace']['_recent'] = []

        replace = Event("__.r__")
        replace.define(msg_definition=".*")
        replace.subscribe(self)

        self.bot.register_event(replace, self)

        self.help = ".replay <number of lines | optional>"
        self.MAX_BUFFER_SIZE = 300
        self.MAX_HISTORY_SIZE = 10

    def get_replacement_message(self, channel=None, find_msg=''):
        """Looks through the mem_store to find the most recent message containing find_msg"""
        if not channel:
            print("couldnt find channel")
            return None
        # must have at least one msg to search for and channel to look it up in
        if len(find_msg) == 0 or not channel:
            print("find_msg is empty")
            return None
        # search for a matching string and saves the index of that entry.
        # Searches from most recent to oldest.
        found_index = -1
        for index, line in enumerate(self.bot.mem_store['replace'][channel]):
            message = line.decode('utf-8', 'ignore')
            msg_index = message.find(">")
            message = message[msg_index:]
            print(line)
            # if the current entry of mem_store contains our string, we set the
            # index and then BREAK to stop looking
            if find_msg.decode('utf-8', 'ignore') in message:
                found_index = index
                break
        # check to see if index values are positive. if not, string was not
        # found and we're done
        if found_index == -1:
            print("couldnt find a good match")
            return None
        # returns the entire line
        submission = self.bot.mem_store['replace'][channel][found_index]
        return submission

    def is_number(self, e):
        try:
            int(e)
            return True
        except ValueError:
            return False

    def handle(self, event):
        # first we see if we're going to try a replace or just add a line to
        # the mem_store
        if event.msg.startswith(".replay "):
            msg = event.msg.replace('.replay ', '')
            user = event.user
            msglist = self.bot.mem_store['replace'][event.channel]
            l = len(msglist)
            if self.is_number(msg):
                msg = int(msg)
                if msg > l:
                    msg = l - 1
                self.printer(
                    "PRIVMSG " +
                    event.channel +
                    ' :' +
                    user +
                    ", I'm sending you a message with the last " +
                    repr(msg) +
                    ' recorded messages. \n')
            else:
                self.printer(
                    "PRIVMSG " +
                    event.channel +
                    ' :Invalid argument \n')

            x = msg
            while x >= 1:
                self.printer("PRIVMSG " + user + ' :' + msglist[x] + '\n')
                x = x - 1

            #msg_index = newString.find(">")
            #message = newString[msg_index + 2:]
            ##message = message.replay(find_msg, replace_msg)
            #user = newString[1:msg_index]
            # pybot sends the new replacement message to the chat
            #self.printer("PRIVMSG " + event.channel + ' :' + user + " MEANT to say: " + message + '\n')
