from event import Event
import meme_credentials
import random
import difflib
import time
import re

try:
  import requests
except ImportError:
  print "Warning: meme module requires requests."
  requests = object

"""
the imgflip api requires credentials, which are bad to put directly into source code. in order to use this module, you will need a file in modules/ called meme_credentials, whose content follows this pattern:

class MemeCredentials:
  imgflip_userid = "YOUR_USERID"
  imgflip_password = "YOUR_PASSWORD"

Dassit.
"""

class meme:
    def __init__(self, events=None, printer_handle=None, bot=None, say=None):
        self.events = events
        self.printer = printer_handle
        self.interests = ['__privmsg__']# should be first event in the listing.. so lines being added is a priority
        self.bot = bot
        self.say = say
        self.imgflip_userid = meme_credentials.MemeCredentials.imgflip_userid
        self.imgflip_password = meme_credentials.MemeCredentials.imgflip_password
        self.top_memes_list = self.get_top_memes()
        self.cmd = ".meme"
        self.help = ".meme [[meme name] [| nick to use for history]]"
        self.ignore_list = [self.bot.NICK, 'TSDBot', 'Bonk-Bot']
        self.ignore_nicks = self.create_ignore_nicks_tuple()
        self.RATE_LIMIT = 300 #rate limit in seconds
        self.bot.mem_store['meme'] = {}

        for event in events:
          if event._type in self.interests:
            event.subscribe(self)


    def get_top_memes(self):
        """Makes an API call to imgflip to get top 100 most popular memes. Returns a list of results"""
        url = "https://api.imgflip.com/get_memes"
        try:
            top_memes = requests.get(url)
        except ConnectionError, e:
            self.bot.debug_print("ConnectionError in get_top_memes(): ")
            self.bot.debug_print(str(e))
        #check for HTTP errors
        try:
            top_memes.raise_for_status()
        except requests.exceptions.HTTPError, e:
            self.bot.debug_print("HTTPError in get_top_memes(): ")
            self.bot.debug_print(str(e))
            return
        #return list if successful
        try:
            top_memes_list = top_memes.json()['data']['memes']
            return top_memes_list
        except KeyError, e:
            self.bot.debug_print("KeyError in get_top_memes(): ")
            self.bot.debug_print(str(e))
            return

    def create_ignore_nicks_tuple(self):
        """creates a tuple with all nicks from self.ignore_list in <>"""
        nick_list = []
        for nick in self.ignore_list:
            nick_list.append("<"+nick+">")
        return tuple(nick_list)

    def get_random_meme_id(self):
        """Selects a random id from the top_memes_list"""
        try:
            return random.choice(self.top_memes_list)['id']
        except KeyError, e:
            self.bot.debug_print("KeyError in get_random_meme_id(): ")
            self.bot.debug_print(str(e))
            return

    def compare_description(self, meme_name, user_description):
        """compares two strings. if greater than 67% similarity, returns true"""
        comparison = difflib.SequenceMatcher()
        comparison.set_seq1(meme_name.lower())
        comparison.set_seq2(user_description.lower())
        if comparison.ratio() >= 0.67:
            return True
        return False

    def get_specific_meme_id(self, user_description):
        """finds a meme_id based on user's description. if not found, selects randomly"""
        try:
            for meme in self.top_memes_list:
                if self.compare_description(meme['name'], user_description):
                    return meme['id']
        except (IndexError, KeyError), e:
            self.bot.debug_print("KeyError in get_specific_meme_id(): ")
            self.bot.debug_print(str(e))
        return None

    def get_line(self, array_of_lines):
        """Given an array of lines from which to pick,  randomly
        select an appropriate line, clean it up, and return the string."""
        line = ""
        #our counter so we don't get caught in an infinite loop when too few good lines exist
        counter = 0
        #make sure we get a line from someone speaking
        try:
            while not line.startswith("<") and counter < 20:
                counter += 1
                line = random.choice(array_of_lines)
                formatted_line = self.format_string(line)
                #discard any lines with .commands or said by ignored nicks. those aren't any fun
                #also discard lines that contain a URL
                if formatted_line.startswith(".") or line.startswith(self.ignore_nicks) or self.contains_url(line):
                    line = ""
        except KeyError, e:
            self.bot.debug_print("KeyError in get_random_line(): ")
            self.bot.debug_print(str(e))
            return
        #format the string for use in the meme and return it
        return formatted_line

    def get_user_lines(self, channel, nick):
        """Given a specific nick and channel, create a list of all their lines in the buffer"""
        line_list = []
        for line in self.bot.mem_store['qdb'][channel]:
            if line.lower().startswith("<"+nick.lower()+">"):
                line_list.append(line)
        return line_list


    def format_string(self, line):
        """Given an appropriate line, strip out <nick>"""
        if line.startswith("<"):
            return line.split("> ", 1)[1]
        else:
            return line

    def create_meme(self, meme_id, top_line, bottom_line):
        """Given a meme id from imgflip and two lines, top and bottom, submit a request
        to imgflip for a new meme and return the URL"""
        url = "https://api.imgflip.com/caption_image"
        payload = {'template_id':meme_id, 'username':self.imgflip_userid, 
                   'password':self.imgflip_password, 'text0':top_line, 'text1':bottom_line}
        try:
            meme = requests.post(url, payload)
        except ConnectionError, e:
            self.bot.debug_print("ConnectionError in create_meme(): ")
            self.bot.debug_print(str(e))
            return
        #check for HTTP errors
        try:
            meme.raise_for_status()
        except request.exceptions.HTTPError, e:
            self.bot.debug_print("HTTPError in create_meme(): ")
            self.bot.debug_print(str(e))
            return
        try:
            return meme.json()['data']['url']
        except KeyError, e:
            self.bot.debug_print("KeyError in create_meme(): ")
            self.bot.debug_print(str(e))
            return

    def get_last_meme_time(self, nick):
        """Given a channel name, return the last time .meme was called in that channel, return 0 if never used"""
        try:
            return self.bot.mem_store['meme'][nick]
        except KeyError:
            self.set_last_meme_time(nick)
            return 0

    def set_last_meme_time(self, nick):
        """Upon calling meme, set the last time it was used by that nick"""
        self.bot.mem_store['meme'][nick] = int(time.time())
        return

    def contains_url(self, line):
        """Given a string, returns True if there is a url present"""
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line)
        if urls:
            return True
        return False

    def check_rate(self, nick):
        """Check to see if the given nick has allowed enough time to pass before calling meme again. Return True and set
           the new last meme time if true. Warn nick and return False if not."""
        time_diff = int(time.time()) - self.get_last_meme_time(nick)
        if time_diff > self.RATE_LIMIT:
            self.set_last_meme_time(nick)
            return True
        else:
            self.say(nick, "WOOP WOOP! Meme Police! You must wait " + str(self.RATE_LIMIT - time_diff) + " seconds to use .meme again.")
            return False
      
    def get_random_flavor(self):
        """Change up the flavor text when returning memes. It got boring before"""
        flavors = ["Tip top: ",
                   "Only the dankest: ",
                   "It's a trap!: ",
                   "[10] outta 10: ",
                   "A mastapeece: ",
                   "Not sure if want: ",
                   "*holds up spork*: ",
                   "Da Fuq?: "
                  ]
        return random.choice(flavors)



    def handle(self, event):
        if event.msg.startswith(".meme"):
            #just return help. we won't bother people with rate limits for this
            if event.msg == ".meme help":
                self.say(event.channel, "Top meme descriptions here: https://api.imgflip.com/popular_meme_ids")
                self.say(event.channel, "Usage: .meme [[description of meme image] [| nick of user to pull lines from]]")
                return
            
            #check the rate first, then continue with processing
            if self.check_rate(event.user):
                #just a random meme please
                if event.msg == ".meme":
                    line_array = self.bot.mem_store['qdb'][event.channel]
                    top_line = self.get_line(line_array)
                    bottom_line = self.get_line(line_array)
                    meme_id = self.get_random_meme_id()
                    meme_url = self.create_meme(meme_id, top_line, bottom_line)
                    if(meme_url):
                        self.say(event.channel, self.get_random_flavor() + meme_url)
                    else:
                        self.say(event.channel, "Error making memes. What a bummer.")
                    return
                #more detail requested
                else:
                    args = event.msg[5:].split("|",1)
                    if args[0].strip():
                        meme_id = self.get_specific_meme_id(args[0])
                        if not meme_id:
                            self.say(event.channel, "Bruh, I couldn't find that meme. We'll do a rando.")
                            meme_id = self.get_random_meme_id()
                    else:
                        meme_id = self.get_random_meme_id()
                    if len(args) > 1:
                        line_array = self.get_user_lines(event.channel, args[1].strip())
                        if not line_array:
                            self.say(event.channel, "That memer hasn't spoken or doesn't exist. Using randoms.")
                            line_array = self.bot.mem_store['qdb'][event.channel]
                    else:
                        line_array = self.bot.mem_store['qdb'][event.channel]
                    top_line = self.get_line(line_array)
                    bottom_line = self.get_line(line_array)
                    meme_url = self.create_meme(meme_id, top_line, bottom_line)
                    if meme_url:
                        self.say(event.channel, self.get_random_flavor() + meme_url)
                    else:
                        self.say(event.channel, "It's all ogre. Memery broken.")
                    return
