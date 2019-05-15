#Module created by Bonekin
##Intended to bonk appropriate irc individual in various creative ways##

from event import Event
import random
import sys

try:
  if sys.version_info > (3, 0, 0):
    from .basemodule import BaseModule
  else:
    from basemodule import BaseModule
except (ImportError, SystemError):
  from modules.basemodule import BaseModule

class Bonk(BaseModule):

  def post_init(self):
    bonk = Event("__.bonk__")
    bonk.define(msg_definition="^\.bonk")
    bonk.subscribe(self)
    self.cmd = ".bonk"
    self.help = ".bonk <bonkee>"

    self.bot.register_event(bonk, self) #Subscribe to your event

  def get_bonked(self, bonkee=''): #Randomly selects and returns a string with a bonk action directed toward a given bonkee."

    bonk_actions = [
    'drops a Titan on %s',
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
    'throws a Dorito into %s\'s jugular from the shadows',
    'wub-wubs %s'
    ]
    bonk_action = random.choice(bonk_actions) % bonkee
    return "\001ACTION " + bonk_action


  def handle(self, event):
    _z = event.msg.split() #Splits out the user to be bonked, if there is one, if not it spits out your mistake in proper channel
    if len(_z) == 1:
      self.say(event.channel, "You must specify who you want me to bonk!")
    else:
      self.say(event.channel, self.get_bonked(_z[1]))
