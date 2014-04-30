from event import Event
import random 

class Bonk:
    def __init__(self, events=None, printer_handle=None, bot=None, say=None):
        self.events = events
        self.printer = printer_handle
        self.interests = ['__.bonk__']
        self.bot = bot
        self.say = say

        bonk = Event("__.bonk__")
        bonk.define(msg_definition="^\.bonk")
        bonk.subscribe(self)
        self.bot.register_event(bonk, self)

        self.help = ".bonk <bonkee>" 

    def get_bonked(self, bonkee=''):
        """Randomly selects and returns a string with a bonk action directed toward a given bonkee."""
        bonk_actions = ['drops a Titan on %s',
                       'hadoukens %s',
                       'slaps %s around with a large trout',
                       'slaps %s around wiiIIITTTTHHH.....A HERRING!',
                       'bitch slaps %s',
                       'feeds %s a knuckle sandwich',
                       'sucker punches %s',
                       'drops an ACME anvil on %s',
                       'forces %s to exit the building through the window',
                       'forces %s to watch all the TSD Productions',
                       'roundhouse kicks %s',
                       'bonks %s',
                       'gently caresses %s',
                       'falcon punches %s',
                       'pulls a Mike Tyson on %s\'s ear',
                       'charges up his lazer and fries %s',
                       'introduces %s to his fist',
                       'boinks %s',
                       'immolates %s',
                       'throws %s into the fires of Mount Doom',
                       'ties %s to the railroad tracks, curls his mustache, and grins evilly',
                       'shoryukens %s',
                       'goes medieval on %s',
                       'spoils the endings to popular fiction for %s',
                       'beats %s in Halo 1v1',
                       'ruins %s',
                       'reks %s',
                       'tramples %s under foot',
                       'unleashes his wrath upon %s',
                       'goes all ninja assassin on %s',
                       'beats %s down with the flag and teabags the body',
                       'takes %s\'s mother out for a nice dinner and then never calls her back',
                       'rockets %s from across the map',
                       'telefrags %s',
                       'throws a Dorito into %s\'s jugular from the shadows'
                       ]
        bonk_action = random.choice(bonk_actions) % bonkee
        return "\001ACTION " + bonk_action 

    def handle(self, event):
        _z = str.split(event.msg, None, 1)
        if len(_z) == 1:
            self.printer("PRIVMSG " + event.channel + " :You must specify who you want me to bonk!\n")
            return
        else:
            self.printer("PRIVMSG " + event.channel + " :" + self.get_bonked(_z[1]) + "\001\n")

