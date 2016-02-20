from event import Event
import random 

class Jimmies:
    def __init__(self, events=None, printer_handle=None, bot=None, say=None):
        self.events = events
        self.printer = printer_handle
        self.interests = ['__.jimmies__']
        self.bot = bot
        self.say = say

        jimmies = Event("__.jimmies__")
        jimmies.define(msg_definition="^\.jimmies")
        jimmies.subscribe(self)
        self.bot.register_event(jimmies, self)

        self.help = ".jimmies <nick>" 

    def get_jimmies_status(self):
        """Randomly selects and returns a string with a "jimmies" status."""
        status = [" Rustled [ ] Not Rustled", 
                  "Rustled as fuck", 
                  "Rustled as fuark", 
                  "Rustled 'n' hustled", 
                  "Professor James  R. Russel, Department of Primatology", 
                  "le monkey face", 
                  "No rustling. Only dreams now.", 
                  "Y'all rusting in a jimmies thread", 
                  "Haha. Oh god. Mah jimmies.", 
                  "The jimmies have been compromised.", 
                  "A gorillion jimmies.", 
                  "Boku no rustled", 
                  "Rustle of the Planet of the Jimmies", 
                  "You just rustled my jimmy card", 
                  "Micky Rourke as The Rustler", 
                  ">he thinks his jimmies are unrustled", 
                  "WWE Rustlemania", 
                  "Teach Me How To Jimmie", 
                  "#3 Rustle Wilson", 
                  "Rustle-it Ralph", 
                  "All those people. All that rustling.", 
                  "Rustle Brand", 
                  "Everyone's getting rustled!", 
                  "Did someone rustle your jimmies? Show me on the doll where they rustled you.", 
                  "Oh shit! My jimmies!"
                  ]
        return "[X] " + random.choice(status)

    def handle(self, event):
        _z = event.msg.split(None, 1)
        jimmies_status = self.get_jimmies_status()
        try:
            self.say(event.channel, "Jimmies status for " + _z[1]+ ": " + jimmies_status)
        except IndexError:
            self.say(event.channel, "You didn\'t specify whose jimmies you wanted to check. " + event.user + "\'s jimmies status: " + jimmies_status) 
        except TypeError:
            print "DEBUG: TypeError: ",
            print event.channel,
            print event.user
