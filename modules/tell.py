# utility class for Tell
class Notice:
  def __init__(self, subj, obj, message):
    self.subject = subj
    self.obj = obj
    self.message = message

class Tell:
  def __init__(self, events=None, printer_handle=None, bot=None, say=None):
    self.events = events
    self.printer = printer_handle
    self.bot = bot
    self.say = say
    self.interests = ['__privmsg__']

    self.cmd = ".tell"
    self.help = ".tell <nick> <thing to tell when they're back>"

    for event in events:
      if event._type in self.interests:
        event.subscribe(self)

  def handle(self, event):
    #try:
      if event.msg.startswith(".tell"):
        target = event.msg.split()[1]
        thing = event.msg.split()[2:] # all the way to the end
        n = Notice(event.user, target, thing)

        if not "tell" in self.bot.mem_store:
          self.bot.mem_store["tell"] = list()

        # add it to the list of things to tell people
        self.bot.mem_store["tell"].append(n)
        self.printer("PRIVMSG " + event.channel + " :I'll let " + n.obj + " know when they're back. \n")
        
      else:
        if "tell" in self.bot.mem_store:
          for n in self.bot.mem_store["tell"]:
            if event.user.lower() == n.obj.lower():
              self.printer("PRIVMSG " + event.channel + " :Hey " + n.obj + ", " + n.subject + " says \""+ " ".join(n.message) + '\"\n')
              # we've said it, now delete it.
              if n in self.bot.mem_store["tell"]: self.bot.mem_store["tell"].remove(n)
            
      #self.printer("PRIVMSG " + event.channel + " :" + event.user + " spoke " + '\n')
      #print event.user +" talked"
    #except:
    #  #print "DEBUG: TypeError: ",
    #  print event.channel,
    #  print event.user

