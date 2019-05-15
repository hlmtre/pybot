#Tell module created by hlmtre#

from event import Event
try:
  from .basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule

# Utility class for tell module
class Notice:
  def __init__(self, subj, obj, message):
    self.subject = subj
    self.obj = obj 
    self.message = message

class Tell(BaseModule):
  
  def post_init(self):
    """
    Because of the way this module works we have to make sure to set our
    event like we normally would with __.tell__, but we cannot define our
    event with "^\.tell" like we normally would as it will only look for that
    line to trigger the event and the user being told will never receive his message
    since the bot is only looking for .tell and not the user in the PRIVMSG

    We will set the .tell trigger in our handle function "if event.msg.startswith(".tell"):"
    and set define to PRIVMSG so it searches all lines from users. While simultaneously looking
    for the .tell trigger from the user.
    
    This is because we actually need 2 things for this module to work. 

    1.) The user needs to be able to leave a message for someone else using ".tell someuser <Insert message here>" 
    
    2.) The user who the .tell message is directed towards will be determined by the PRIVMSG definition.
        This is determined in the "else" block that searches every line not starting with .tell.
        If the user matches the stored user from the previous tell trigger, the event will be triggered and pybot will spit out text into
        the proper channel every time the intended user says something in chat until the buffer is out of .tell events.
    """

    tell = Event("__.tell__")
    tell.define("PRIVMSG")
    tell.subscribe(self)

    # register ourself to our new custom event
    self.bot.register_event(tell, self)
    
  def handle(self, event):
    try:
      if event.msg.startswith(".tell"):
        target = event.msg.split()[1]
        thing = event.msg.split()[2:]
        if target.lower() == self.bot.conf.getNick(self.bot.network).lower():
          self.say(event.channel, "I can't tell myself; gtfo")
          return
        elif event.user == target:
          self.say(event.channel, "Choose someone that isn't you")
          return
        elif thing == []:
          self.say(event.channel, "I need a message to relay pal")
          return
        n = Notice(event.user, target, thing)

        if not "tell" in self.bot.mem_store:
          self.bot.mem_store["tell"] = list()

        # add it to the list of things to tell people
        self.bot.mem_store["tell"].append(n)
        self.say(event.channel, "I'll let " + n.obj + " know when they're back.")

      else:
        if "tell" in self.bot.mem_store:
          for n in self.bot.mem_store["tell"]:
            if event.user.lower() == n.obj.lower():
              self.say(event.channel, "Hey " + n.obj + ", " + n.subject + " says \""+ " ".join(n.message)+"\"")
              # we've said it, now delete it.
              self.bot.mem_store["tell"].remove(n)
    except IndexError:
      self.say(event.channel, "You need to tell me what to say....idjit")
