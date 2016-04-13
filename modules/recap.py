# -*- coding: utf-8 -*-

from event import Event
import random
import string
import time
import re

try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule

class recap(BaseModule):
    def post_init(self):
        self.interests = ['__privmsg__']# should be first event in the listing.. so lines being added is a priority
        self.cmd = ".recap"
        self.help = ".recap"
        self.ignore_list = [self.bot.NICK, 'TSDBot', 'Bonk-Bot']
        self.ignore_nicks = self.create_ignore_nicks_tuple()
        self.RATE_LIMIT = 600 #rate limit in seconds
        self.MIN_WORDS = 4 #we want at least this many words for a valid line
        self.RECAP_LENGTH = 4 #number of lines to include in recap
        self.bot.mem_store['recap'] = {}

        for event in self.events:
          if event._type in self.interests:
            event.subscribe(self)

    def create_ignore_nicks_tuple(self):
        """creates a tuple with all nicks from self.ignore_list in <>"""
        nick_list = []
        for nick in self.ignore_list:
            nick_list.append("<"+nick+">")
        return tuple(nick_list)

    def get_lines(self, channel):
        """Given a channel, searches the qdb buffer for 4 random, suitable lines."""
        try:
            #create a copy of the channel buffer
            lines = list(self.bot.mem_store['qdb'][channel])
            #shuffle that copy up randomly
            random.shuffle(lines)
            recap = []
            while len(lines)>0 and len(recap) < self.RECAP_LENGTH:
                #as long as we have lines in the buffer and haven't chosen the desired number
                #keep popping lines off the top of the scrambled buffer
                #this ensures no duplicates ever are chosen
                line = lines.pop()
                #test for validity and add to our array of valid lines
                if self.valid_line(line):
                    parts = line.split(None, 1)
                    recap.append(self.scramble_nick(parts[0]) + " " + self.dramatize_line(parts[1]))
            return recap
        except Exception as e:
            self.bot.debug_print("Error getting channel buffer in get_lines")
            self.bot.debug_print(str(e))
            return False

    def valid_line(self, line):
        """Returns True if a given line matches all requirements for validity:
           Not an action line, longer than minimum length, not spoken by ignored nicks, no URLs"""
        #easy check to see if it's a line of someone speaking
        if line.startswith("<"):
            if not (line.startswith(self.ignore_nicks) or 
                    self.contains_url(line) or 
                    len(line.split()) < self.MIN_WORDS or
                    line.split(None,1)[1].startswith((".","#","s/"))): 
                return True
        return False

    def dramatize_line(self, line):
        """Pass a valid line in, return line with some random type of dramatic formatting"""
        drama = random.randint(0,750) #choose a random number
        line = line.strip()
        try:
            if drama in range(100,200):
                return line + "??"
            elif drama in range(200,300):
                return line + "..."
            elif drama in range(300,400):
                return line.upper()
            elif drama in range(400,500):
                return line + "!!"
            elif drama in range(500,550):
                return line.upper() + "!!"
            elif drama in range(550,600):
                return line.upper() + "?!?"
            elif drama in range(600,700):
                return line + " ~"
            elif drama in range(700,750):
                listline = list(line)
                for x in range(0, len(listline), 2):
                    listline[x] = listline[x].upper()
                return ''.join(listline)
            elif drama == 69:
                return u'( ͡° ͜ʖ ͡°) (ง ͠° ͟ل͜ ͡°)ง ᕦ( ͡° ͜ʖ ͡°)ᕤ ( ͡~ ͜ʖ ͡°)'
            elif drama == 750:
                return line[::-1] #reversed string
            else:
                return line
        except:
            return line

    def scramble_nick(self, nick):
        """Given a valid nick in the format <nickname>, scramble a vowel in the nick to avoid beeping the user"""
        try:
            vowels = 'aeiou'
            nick_vowels = []
            nick_letters = list(nick[1:-1]) #grab the nick from between <> and conver to a list to make changes
            #create a list of tuples. each tuple is (index of a vowel in nick, the vowel at that index)
            for i,v in enumerate(nick_letters):
                if v.lower() in vowels:
                    nick_vowels.append((i,v))
            #randomly choose one of the vowels in the nick to replace
            sel = random.choice(nick_vowels)
            #randomly select any vowel
            repl = random.choice(vowels)
            #keep doing the previous line until we get something different from what we're replacing
            while repl == sel[1].lower():
                repl = random.choice(vowels)
            #if the chosen letter to be replaced is upper case, make sure the replacement is too
            if nick_letters[sel[0]].isupper():
                nick_letters[sel[0]] = repl.upper()
            else:
                nick_letters[sel[0]] = repl
            #take that list of individual characters and slam it all back together into a string surrounded by <>
            nick = '<' + ''.join(nick_letters) + '>'  
            #take the old nick out of the submitted line and replace it with the new scramble one
            return nick
        except IndexError: # no vowels, probably
            #self.bot.debug_print("Error scrambling nick. Just moving on. Nick was: " + original_nick, error=True)
            return nick #if there's any problems at all, just don't scramble the nick. odd cases like no vowels

    def contains_url(self, line):
        """Given a string, returns True if there is a url present"""
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line)
        if urls:
            return True
        return False

    def check_rate(self, channel):
        """Check to see if the given channel has allowed enough time to pass before calling recap again. Return True 
           and set the new time limit if true. Return False if not."""
        try:
            if self.get_timediff(channel) <= 0: 
                self.bot.mem_store['recap'][channel] = int(time.time()) + self.RATE_LIMIT
                return True
            else:
                return False
        except KeyError:
            self.bot.mem_store['recap'][channel] = int(time.time()) + self.RATE_LIMIT
            return True
    
    def reset_timer(self, channel):
        """If there's an error getting a recap, call this to reset lockdown timer"""
        self.bot.mem_store['recap'][channel] = int(time.time())

    def get_timediff(self, channel):
        """Return how much time remains in the function lockdown"""
        return self.bot.mem_store['recap'][channel] - int(time.time())
      
    def get_episode(self):
        """Return a list with two elements: a random show title and episode name"""
        titles = ["Internet Relay Chat",
                  "Multiplayer Notepad",
                  "Wise Use of Work Hours",
                  "The Kanbo Korner",
                  "2 Grils?",
                  "Exodus",
                  "Tex's Tricks",
                  "Top Fun",
                  "Big Anime Robots",
                  "The Meme Machine",
                  "The Botpocalypse",
                  "IRC",
                  "St. Paddy's",
                  "Get Bonked",
                  "Schooly's Skills",
                  "D O R D R A Y",
                  "GET BIG",
                  "AYYYY",
                  "Corgis"
                  ]
        episodes = ["The Mystery of DeeJ",
                    "Paddy's Big Goodbye",
                    "Hickory Dickory...Dead",
                    "BoneKin Dies",
                    "Dr. DeeJ and Mr. DorJ",
                    "The Double Dorj",
                    "Bonk-Bot's Crash Test Dummies",
                    "IRC Finds a Dead Body",
                    "Beach Party",
                    "Everyone Gets Sucked Back in Time",
                    "Brass Tax",
                    "Return to Bonk Mountain",
                    "The Incredible Bonk",
                    "Paddy Gets Big",
                    "Dawn of the New Age",
                    "Tex Goes to Work",
                    "Planet of the IRC",
                    "Nart Gets His GED",
                    "High School Drama",
                    "TD Moves Out",
                    "TDSpiral Paints a Picture",
                    "Kapowaz Wins",
                    "Banana Gets High",
                    "Dragon's Laird",
                    "StarLaird",
                    "Kanboface",
                    "Eternity, Loyalty, Honesty",
                    "Paddy on Parole",
                    "The HBO Beauty Contest, Pt. 2",
                    "Snipe Reviews Halo 5",
                    "1-800-GET-GOOD",
                    "A Baby Wheel",
                    "BoneKin Ruins the Creative Process",
                    "The 80 Proof Spoof",
                    "IRC Forgets to Set Their Holiday Nicks",
                    "Hot Diggety Dorj",
                    "Yapok Talks",
                    "Hellmitre Argues With His Bot",
                    "Pybot Strikes Back",
                    "Where's Schooly?",
                    "Heavy Is the BanHammer",
                    "Sunbreaker or Sunbroken?",
                    "Testing in Production",
                    "BoneKin Codes a New Module and Forgets How to Use Git",
                    "The Curse of the Spiduh",
                    "Snipe Quits Halo (Part 2)",
                    "Monopoly Is A Fun Game",
                    "RAWR",
                    "Jennos Has A Cow",
                    "Pybot Steals TSDBot's Modules",
                    "Paddy on Patrol",
                    "Schooly's Return",
                    "The PUNisher",
                    "Dr. GV, PhD, although I guess if he was a medical doctor he wouldn't have a PhD? Or maybe they can, I don't know. I know he'd be called 'Dr.' though. I think they should make that clearer, like in the dictionary or wherever they spell things out like that. But I guess it wouldn't be an English thing it'd be a medical licensing and terminology thing? Uuuuuuugggggghhhh it's already so late and I was supposed to go to bed 23 minutes ago but then t"
                    ]
                    
        return [random.choice(titles), random.choice(episodes)]



    def handle(self, event):
        if event.msg == ".recap":
            #check the rate first, then continue with processing
            if self.check_rate(event.channel):
                episode = self.get_episode()
                recap = self.get_lines(event.channel)
                if not recap:
                    self.reset_timer(event.channel)
                    self.say(event.channel, "Error processing recap request")
                    return
                self.say(event.channel, "Previously on \"" + episode[0] + "\": ")
                for r in recap:
                    self.say(event.channel, r)
                self.say(event.channel, "Tonight's episode: \"" + episode[1] + "\"")
            else:
                timediff = str(self.get_timediff(event.channel))
                self.say(event.user, "Recap is on lockdown for " + timediff + " more seconds.")
