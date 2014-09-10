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

    def get_told_status(self, target):
        """Randomly selects and returns a string with a "told" status."""
        status = ["FUCKING TOLD",
                  "CASH4TOLD.COM",
                  "KNIGHTS OF THE TOLD REPUBLIC",
                  "STONE TOLD STEVE AUSTIN",
                  "CURE FOR THE COMMON TOLD",
                  "BEN TOLDS FIVE",
                  "THE 40 YEAR TOLD VIRGIN",
                  "TOLDENEYE 007",
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
                  "CALIFORNIA TOLD RUSH",
                  "THERE'S TOLD IN THEM THAR HILLS"
                  ]
        exclamation = ["Damn!",
                       "Damn, son!",
                       "Snap!",
                       "Sheeeiiiiittttt.",
                       "Ouch!"
                      ]
        return random.choice(exclamation) + " %s\'s told status: [X] " % target + random.choice(status)

    def handle(self, event):
        _z = str.split(event.msg, None, 1)
        try:
            self.say(event.channel, self.get_told_status(_z[1]))
        except IndexError:
            self.say(event.channel, "You didn\'t say who got told!")
            self.say(event.channel, self.get_told_status(event.user))
