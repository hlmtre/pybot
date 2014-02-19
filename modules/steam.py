import steamapi
import cPickle as pickle

class Steam:
  def __init__(self, events=None, printer_handle=None, bot=None):
    self.events = events
    self.printer = printer_handle
    self.interests = ['__.steam__']
    self.bot = bot
    for event in events:
      if event._type in self.interests:
        event.subscribe(self)

  def handle(self, event):
    if "steam" not in self.bot.mem_store:
      self._importpickle()

    steamapi.core.APIConnection(api_key="4FE154D08A234F786A64D05E78B4280D")
    me = steamapi.user.SteamUser(76561197996289741)
    msg = event.line.split(":",2)[2]
    if msg.startswith(".steam set"):
      if not "steam" in self.bot.mem_store:
        self.bot.mem_store["steam"] = dict()

      try: 
        self.bot.mem_store["steam"][msg.split()[2]] = msg.split()[3]
        pickle.dump(self.bot.mem_store["steam"], open("steamdict.p","w+b"))
        #print pickle.dumps(self.bot.mem_store["steam"])
      except IndexError:
        self.printer("PRIVMSG " +event.channel + " :Error! Need username to save under and steam ID number. \n")
        return

    if msg.startswith(".steam list"):
      for entry,key in self.bot.mem_store["steam"].items():
        self.printer("PRIVMSG " +event.channel + " :" + entry + " -- " + key + "\n")
 
  def _importpickle(self):
    try:
      print "attempting import"
      self.bot.mem_store["store"] = pickle.load(open("steamdict.p","rb"))
    except IOError:
      pass
