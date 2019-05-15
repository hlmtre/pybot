from event import Event
import random
import difflib
import time
import re

try:
    import requests
except (ImportError, SystemError):
    print("Warning: meme module requires requests.")
    requests = object

try: 
    from meme_credentials import MemeCredentials as mc
except (ImportError, SystemError):
    print("Warning: meme module requires credentials in modules/meme_credentials.py")
    class PhonyMc:
        imgflip_userid = "None"
        imgflip_password = "None"
    mc = PhonyMc()

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
        self.imgflip_userid = mc.imgflip_userid
        self.imgflip_password = mc.imgflip_password
        self.top_memes_list = self.get_top_memes()
        self.cmd = ".meme"
        self.help = ".meme [nickname]"
        self.ignore_list = [self.bot.NICK, 'TSDBot', 'Bonk-Bot']
        self.ignore_nicks = self.create_ignore_nicks_tuple()
        self.RATE_LIMIT = 30 #rate limit in seconds
        self.bot.mem_store['meme'] = {}

        for event in events:
          if event._type in self.interests:
            event.subscribe(self)


    def get_top_memes(self):
        """Makes an API call to imgflip to get top 100 most popular memes. Returns a list of results"""
        url = "https://api.imgflip.com/get_memes"
        try:
            top_memes = requests.get(url)
        except ConnectionError as e:
            self.bot.debug_print("ConnectionError in get_top_memes(): ")
            self.bot.debug_print(str(e))
        #check for HTTP errors
        try:
            top_memes.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self.bot.debug_print("HTTPError in get_top_memes(): ")
            self.bot.debug_print(str(e))
            return
        #return list if successful
        try:
            top_memes_list = top_memes.json()['data']['memes']
            return top_memes_list
        except KeyError as e:
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
        except KeyError as e:
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

    def get_line(self, array_of_lines):
        """Given an array of lines from which to pick, randomly
        select an appropriate line, clean it up, and return the string."""
        line = ""
        #our counter so we don't get caught in an infinite loop when too few good lines exist
        counter = 0
        #make sure we get a line from someone speaking
        try:
            while not line.startswith("<") and counter < 20:
                counter += 1
                line = random.choice(array_of_lines)
                if not self.is_valid_line(line): 
                    line = ""
        except Exception as e:
            self.bot.debug_print("Error in get_random_line(): ")
            self.bot.debug_print(str(e))
            return
        #format the string for use in the meme and return it
        return self.format_string(line)

    def is_valid_line(self, line):
        """Given a line from the qdb buffer, return True if certain conditions are met
        that make it good for meme selection. Return False if not"""
        formatted_line = self.format_string(line) #strips the nick off the beginning
        if (formatted_line.startswith(".") or       #reject .commands
            formatted_line.startswith("#") or       #reject #commands meant for BonkBot
            formatted_line.startswith("s/") or       #reject s// substitution lines
            self.contains_url(line) or              #reject lines with URLs
            line.startswith(self.ignore_nicks) or   #reject lines spoken by bots
            "TSDBot" in line):    #reject any line with "TSDBot" due to mass printout summoning
            return False
        return True

    def get_user_lines(self, channel, nick):
        """Given a specific nick and channel, create a list of all their lines in the buffer"""
        line_list = []
        for line in self.bot.mem_store['qdb'][channel]:
            if line.lower().startswith("<"+nick.lower()+">"):
                line_list.append(line)
        return line_list


    def format_string(self, line):
        """Given an appropriate line, strip out <nick>. Otherwise return unmodified line"""
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
        except ConnectionError as e:
            self.bot.debug_print("ConnectionError in create_meme(): ")
            self.bot.debug_print(str(e))
            return
        #check for HTTP errors
        try:
            meme.raise_for_status()
        except request.exceptions.HTTPError as e:
            self.bot.debug_print("HTTPError in create_meme(): ")
            self.bot.debug_print(str(e))
            return
        try:
            return meme.json()['data']['url']
        except KeyError as e:
            self.bot.debug_print("KeyError in create_meme(): ")
            self.bot.debug_print("User: " + self.imgflip_userid + " Password: " + self.imgflip_password)
            self.bot.debug_print(str(e))
            self.bot.debug_print(str(meme.json()))
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
            if not self.check_rate(event.user):
              return
            #just a random meme please
            if event.msg == ".meme":
                line_array = self.bot.mem_store['qdb'][event.channel]
                top_line = self.get_line(line_array)
                bottom_line = self.get_line(line_array)
            #more detail requested
            else:
                nick = event.msg[5:].strip().split(None)[0]
                line_array = self.get_user_lines(event.channel, nick)
                if not line_array:
                    self.say(event.channel, "That memer hasn't spoken or doesn't exist. Using randoms.")
                    line_array = self.bot.mem_store['qdb'][event.channel]
                top_line = self.get_line(line_array)
                bottom_line = self.get_line(line_array)

            meme_id = self.get_random_meme_id()
            meme_url = self.create_meme(meme_id, top_line, bottom_line)
            if meme_url:
                self.say(event.channel, self.get_random_flavor() + meme_url)
            else:
                self.say(event.channel, "It's all ogre. Memery broken.")
                return
