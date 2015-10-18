from event import Event
import random
import difflib

"""try:
  import imgurpython
except ImportError:
  print "Warning: meme module requires imgurpython."
  imgurpython = object
"""

try:
  import requests
except ImportError:
  print "Warning: meme module requires requests."
  requests = object


class meme:
    def __init__(self, events=None, printer_handle=None, bot=None, say=None):
        self.events = events
        self.printer = printer_handle
        self.interests = ['__privmsg__']# should be first event in the listing.. so lines being added is a priority
        self.bot = bot
        self.say = say
        self.imgflip_userid = ""
        self.imgflip_password = ""
        self.top_memes_list = self.get_top_memes()
        self.cmd = ".meme"
        self.help = ".meme [[meme name] [| nick to use for history]]"
        self.ignore_list = [self.bot.NICK, 'TSDBot']
        self.ignore_nicks = self.create_ignore_nicks_tuple()

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
        comparison.set_seq1(meme_name)
        comparison.set_seq2(user_description)
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
                if formatted_line.startswith(".") or line.startswith(self.ignore_nicks):
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
            if line.startswith("<"+nick+">"):
                line_list.append(line)
        return line_list


    def format_string(self, line):
        """Given an appropriate line, strip out <nick>"""
        self.bot.debug_print(line)
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
      
    def handle(self, event):
        #to begin with, all memes are random. this will change later
        if event.msg.startswith(".meme"):
            #just a random meme please
            if event.msg == ".meme":
                line_array = self.bot.mem_store['qdb'][event.channel]
                top_line = self.get_line(line_array)
                bottom_line = self.get_line(line_array)
                meme_id = self.get_random_meme_id()
                meme_url = self.create_meme(meme_id, top_line, bottom_line)
                if(meme_url):
                    self.say(event.channel, "Tip top meme: " + meme_url)
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
                else:
                    line_array = self.bot.mem_store['qdb'][event.channel]
                top_line = self.get_line(line_array)
                bottom_line = self.get_line(line_array)
                meme_url = self.create_meme(meme_id, top_line, bottom_line)
                if meme_url:
                    self.say(event.channel, "Only the dankest memes: " + meme_url)
                else:
                    self.say(event.channel, "It's all ogre. Memery broken.")
                return
