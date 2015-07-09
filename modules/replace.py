##NEEDS
#adding a bold character for '<user> MEANT so say'

from event import Event
import requests
import difflib

class Replace:
  def __init__(self, events=None, printer_handle=None, bot=None, say=None):
    self.events = events
    self.printer = printer_handle
    self.interests = ['__.replace__'] 
    self.bot = bot
    self.say = say

    self.bot.mem_store['replace'] = {}
    #define a key for _recent since that will not be a potential channel name
    self.bot.mem_store['replace']['_recent'] = []

    replace = Event("__.r__")
    replace.define(msg_definition=".*")
    replace.subscribe(self)

    self.bot.register_event(replace, self)

    self.help = ".r <search string> | <replacement text>"
    self.MAX_BUFFER_SIZE = 300 
    self.MAX_HISTORY_SIZE = 10

  def add_buffer(self, event=None, debug=False): 
    """Takes a channel name and line passed to it and stores them in the bot's mem_store dict
    for future access. The dict will have channel as key. The value to that key will be a list
    of formatted lines of activity. 
    If the buffer size is not yet exceeded, lines are just added. If the buffer
    is maxed out, the oldest line is removed and newest one inserted at the beginning.
    """
    if debug:
      print "Line: " + event.line
      print "Verb: " + event.verb
      print "Channel: " + event.channel
      print ""
    if not event:
      return
    #there are certain things we want to record in history, like nick changes and quits
    #these often add to the humor of a quote. however, these are not specific to a channel
    #in IRC and our bot does not maintain a userlist per channel. Therefore, when nick
    #changes and quits occur, we will add them to every buffer. This is not technically
    #correct behavior and could very well lead to quits/nick changes that are not visible
    #showing up in a quote, but it's the best we can do at the moment
    if not event.channel:
      #discard events with unwanted verbs 
      if event.verb not in ["QUIT", "NICK"]:
        return
      try:
        for chan in self.bot.mem_store['replace'].keys():
          if chan != '_recent':
            if len(self.bot.mem_store['replace'][chan]) >= self.MAX_BUFFER_SIZE:
              self.bot.mem_store['replace'][chan].pop()
            line = self.format_line(event)
            if line:
              self.bot.mem_store['replace'][chan].insert(0, line)
      except KeyError, IndexError:
        print "Replace add_buffer() error when no event channel"
    #now we continue with normal, per channel line addition
    #create a dictionary associating the channel with an empty list if it doesn't exist yet
    else:
      if event.channel not in self.bot.mem_store['replace']:
        self.bot.mem_store['replace'][event.channel] = []
      try:
      #check for the length of the buffer. if it's too long, pop the last item
        if len(self.bot.mem_store['replace'][event.channel]) >= self.MAX_BUFFER_SIZE:
          self.bot.mem_store['replace'][event.channel].pop()
        #get a line by passing event to format_line
        #insert the line into the first position in the list
        line = self.format_line(event) 
        if line:
          self.bot.mem_store['replace'][event.channel].insert(0, line)
      except IndexError:
        print "Replace add_buffer() error. Couldn't access the list index."

  def format_line(self, event):
    """Takes an event and formats a string appropriate for quotation from it"""
    #format all strings based on the verb
    if event.verb == "":
      return ''
    elif event.verb == "PRIVMSG":
      #special formatting for ACTION strings
      if event.msg.startswith('\001ACTION'): 
        #strip out the word ACTION from the msg
        return ' * %s %s\n' % (event.user, event.msg[7:])
      else:
        return '<%s> %s\n' % (event.user, event.msg)
    elif event.verb == "JOIN":
      return ' --> %s has joined channel %s\n' % (event.user, event.channel)
    elif event.verb == "PART":
      return ' <-- %s has left channel %s\n' % (event.user, event.channel)
    elif event.verb == "NICK":
      return ' -- %s has changed their nick to %s\n' % (event.user, event.msg)
    elif event.verb == "TOPIC":
      return ' -- %s has changed the topic for %s to "%s"\n' % (event.user, event.channel, event.msg)
    elif event.verb == "QUIT":
      return ' <-- %s has quit (%s)\n' % (event.user, event.msg)
    elif event.verb == "KICK":
      #this little bit of code finds the kick target by getting the last
      #thing before the event message begins
      target = event.line.split(":", 2)[1].split()[-1]
      return ' <--- %s has kicked %s from %s (%s)\n' % (event.user, target, event.channel, event.msg)
    elif event.verb == "NOTICE": 
      return ' --NOTICE from %s: %s\n' % (event.user, event.msg)
    else:
      #no matching verbs found. just ignore the line
      return ''

  def get_replacement_message(self, channel=None, find_msg=''):
    """Looks through the mem_store to find the most recent message containing find_msg"""
    if not channel:
      #print "couldnt find channel"
      return None
    #must have at least one msg to search for and channel to look it up in
    if len(find_msg) == 0 or not channel:
      #print "find_msg is empty"
      return None
    #search for a matching string and saves the index of that entry. 
    #Searches from most recent to oldest.
    found_index = -1
    for index, line in enumerate(self.bot.mem_store['replace'][channel]):
      message = line
      msg_index = message.find(">")
      message = message[msg_index:]
      #print line
      #if the current entry of mem_store contains our string, we set the index and then BREAK to stop looking
      if find_msg.decode('utf-8','ignore') in message:
        found_index = index
        break
    #check to see if index values are positive. if not, string was not found and we're done
    if found_index == -1 :
      #print "couldnt find a good match"
      return None
    #returns the entire line
    submission = self.bot.mem_store['replace'][channel][found_index]
    return submission
    
  def handle(self, event):
    #first we see if we're going to try a replace or just add a line to the mem_store
    if event.msg.startswith(".r "):
      #split the msg with '.r ' stripped off beginning and divide into a search string and replace string
      string_token = event.msg[3:].split('|', 1)
      find_msg = string_token[0].rstrip()
      try:
        replace_msg = string_token[1].lstrip() #if there's nothing after the pipe, then this resolves to '' which is fine
      except IndexError:
        return
      #looking for a message containing our search string
      newString = self.get_replacement_message(event.channel, find_msg)
      
      #because the mem_store line shows "<user> message", we have to split up the username and their message
      #this actually works to our advantage so we dont have to do additional calls to find out who sent what
      msg_index = newString.find(">")
      message = newString[msg_index + 2:]
      message = message.replace(find_msg, replace_msg)
      user = newString[1:msg_index]
      #pybot sends the new replacement message to the chat
      self.printer("PRIVMSG " + event.channel + ' :' + user + " MEANT to say: " + message + '\n')
    if event.user != self.bot.NICK :
      self.add_buffer(event)
