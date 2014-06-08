from event import Event
import random 

class Told:
    def __init__(self, events=None, printer_handle=None, bot=None, say=None):
        self.events = events
        self.printer = printer_handle
        self.interests = ['__.told__']
        self.bot = bot
        self.say = say

        told = Event("__.told__")
        told.define(msg_definition="^\.told")
        told.subscribe(self)
        self.bot.register_event(told, self)

        self.help = ".told <nick>" 

    def get_told_status(self):
        """Randomly selects and returns a string with a "told" status."""
        status = ["FUCKING TOLD",
                  "CASH4TOLD.COM",
                  "KNIGHTS OF THE TOLD REPUBLIC",
                  "STONE TOLD STEVE AUSTIN",
                  "CURE FOR THE COMMON TOLD",
                  "BEN TOLDS FIVE",
                  "THE 40 YEAR TOLD VIRGIN",
                  "007: TOLDENEYE",
                  "TEXAS TOLD'EM",
                  "AUSTIN POWERS IN TOLDMEMBER",
                  "PTERODACTOLD",
                  "NO COUNTRY FOR TOLD MEN",
                  "24 CARAT TOLD RING",
                  "ONLY SHOOTING STARS BREAK THE TOLD",
                  "GOING ONCE...GOING TWICE...TOLD!",
                  "GARY TOLDMAN",
                  "TOLD SPICE",
                  "TOLD STONE CREAMERY",
                  "BABY IT'S TOLD OUTSIDE",
                  "POKEMON TOLD AND SILVER",
                  "TOLD YELLER",
                  "EL DORADO: THE LOST CITY OF TOLD",
                  "TOLDPLAY",
                  "BATMAN: THE BRAVE AND THE TOLD",
                  "DANNY DEVITOLD",
                  "FOR WHOM THE BELL TOLDS",
                  "CAN'T TEACH A TOLD DOG NEW TRICKS",
                  "I AIN'T SAYING SHE A TOLD DIGGER",
                  "THE TOLDEN COMPASS",
                  "TOLDIER OF FORTUNE",
                  "TOLDING CHAIR",
                  "TOLDEN AXE",
                  "TOLD MACDONALD HAD A FARM",
                  "TOLDEN TOLDIES: HITS FROM THE 50'S, 60'S, AND 70'S",
                  "BATTLETOLDS",
                  "YE TOLDE PUB",
                  "TOLDEN CAULFIELD",
                  "THE TOLD MAN AND THE SEA",
                  "TOLD MEDAL WINNER IN THE WINTER OLYMPICS",
                  "POT OF TOLD AT THE END OF THE RAINBOW",
                  "J.R.R. TOLDKIEN",
                  "THERE'S TOLD IN THEM THAR HILLS"
                  ]
        return "[X] " + random.choice(status)

    def handle(self, event):
        _z = str.split(event.msg, None, 1)
        told_status = self.get_told_status()
        if _z[1].startswith(('.', '#', '!')) and len(str.split(_z[1])) > 1:
            self.say(event.channel, "Nice try, " + event.user + ". Looks like you might be trying to trick me.")
            self.say(event.channel, event.user + "\'s told status: " + told_status)
            return
        try:
            self.printer("PRIVMSG " + event.channel + ' :' + _z[1] + '\'s told status: ' + told_status + '\n')
        except IndexError:
            self.printer("PRIVMSG " + event.channel + ' :You didn\'t say who got told. Your told status: ' + told_status + '\n') 
        except TypeError:
            print "DEBUG: TypeError: ",
            print event.channel,
            print event.user
