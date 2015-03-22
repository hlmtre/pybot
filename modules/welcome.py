from event import Event
from random import choice
class Welcome:
  def __init__(self, events=None, printer_handle=None, bot=None, say=None):
    self.events = events
    self.printer = printer_handle
    self.interests = []
    self.bot = bot

    self.response = ['np', 'you\'re welcome', 'no problem']

    thanks = Event("__thanks__")
    thankyou = Event("__thankyou__")
    nick = self.bot.conf.getNick(self.bot.network)
    thanks.define(msg_definition="^([T|t]hanks) " + nick)
    thankyou.define(msg_definition="^([T|t]hank you) " + nick)
    thanks.subscribe(self)
    thankyou.subscribe(self)

    # register ourself to our new hello event
    self.bot.register_event(thanks, self)
    self.bot.register_event(thankyou, self)

    self.help = None

    # register ourself for any events that we're interested in that exist already
    for event in events:
      if event._type in self.interests:
        event.subscribe(self)

  def handle(self, event):
    try:
      self.bot.brain.say(event.channel, choice(self.response) + " " + event.user + '\n')
    except Exception,e:
      print e

