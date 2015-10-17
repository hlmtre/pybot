from event import Event
import random

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
        self.imgflip_userid = "BoneKin"
        self.imgflip_password = "Djl07jnfe"
        self.top_memes_list = self.get_top_memes()
        self.cmd = ".meme"
        self.help = ".meme"

        for event in events:
          if event._type in self.interests:
            event.subscribe(self)


    def get_top_memes(self):
        """Makes an API call to imgflip to get top 100 most popular memes. Returns a list of results"""
        url = "https://api.imgflip.com/get_memes"
        try:
            top_memes = requests.get(url)
        except ConnectionError, e:
            print "ConnectionError in get_top_memes(): "
            print str(e)
        #check for HTTP errors
        try:
            top_memes.raise_for_status()
        except requests.exceptions.HTTPError, e:
            print "HTTPError in get_top_memes(): "
            print str(e)
            return
        #return list if successful
        try:
            top_memes_list = top_memes.json()['data']['memes']
            return top_memes_list
        except KeyError, e:
            print "KeyError in get_top_memes(): "
            print str(e)
            return

    def get_random_meme_id(self):
        """Selects a random id from the top_memes_list"""
        try:
            return random.choice(self.top_memes_list)['id']
        except KeyError, e:
            print "KeyError in get_random_meme_id(): "
            print str(e)
            return

    def get_random_line(self, channel):
        """Given the channel of the event that triggered the meme generation, randomly
        select an appropriate line, clean it up, and return the string."""
        line = ""
        counter = 0
        #make sure we get a line from someone speaking or performing an action
        try:
            while not line.startswith("<") and counter < 20:
                counter += 1
                line = random.choice(self.bot.mem_store['qdb'][channel])
                formatted_line = self.format_string(line)
                #discard any lines with .commands or said by the bot itself. those aren't any fun
                if formatted_line.startswith(".") or line.startswith("<"+self.bot.NICK+">"):
                    line = ""
        except KeyError, e:
            print "KeyError in get_random_line(): "
            print str(e)
            return
        #format the string for use in the meme and return it
        return formatted_line

    def format_string(self, line):
        """Given an appropriate line from the QDB history buffer, strip out <nick>"""
        print line
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
            print "ConnectionError in create_meme(): "
            print str(e)
            return
        #check for HTTP errors
        try:
            meme.raise_for_status()
        except request.exceptions.HTTPError, e:
            print "HTTPError in create_meme(): "
            print str(e)
            return
        try:
            return meme.json()['data']['url']
        except KeyError, e:
            print "KeyError in create_meme(): "
            print str(e)
            return
      
    def handle(self, event):
        #to begin with, all memes are random. this will change later
        if event.msg.startswith(".meme"):
            top_line = self.get_random_line(event.channel)
            bottom_line = self.get_random_line(event.channel)
            meme_id = self.get_random_meme_id()
            meme_url = self.create_meme(meme_id, top_line, bottom_line)
            if(meme_url):
                self.say(event.channel, "Tip top meme: " + meme_url)
            else:
                self.say(event.channel, "Error making memes. What a bummer.")
        return
