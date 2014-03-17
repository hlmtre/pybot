from event import Event
from random import choice
class Hello:
  def __init__(self, events=None, printer_handle=None, bot=None, say=None):
    self.events = events
    self.printer = printer_handle
    self.interests = []
    self.bot = bot

    self.retorts = ['hello', 'sup', 'hi', 'good to see you', 'loldicks']

    hello = Event("__hello__")
    nick = self.bot.conf.getNick(self.bot.network)
    hello.define(msg_definition="^([H|h]ello|hi|howdy) " + nick)
    hello.subscribe(self)

    # register ourself to our new hello event
    self.bot.register_event(hello, self)

    self.help = None

    # register ourself for any events that we're interested in that exist already
    for event in events:
      if event._type in self.interests:
        print "registering to ", event._type
        event.subscribe(self)

  def handle(self, event):
    try:
      self.bot.brain.say(event.channel, choice(self.retorts) + " " + event.user + '\n')
    except Exception,e:
      print e

