import steamapi
import cPickle as pickle

class Steam:
  def __init__(self, events=None, printer_handle=None, bot=None):
    self.events = events
    self.printer = printer_handle
    self.interests = ['__.steam__']
    self.bot = bot
    self.api_key = "4FE154D08A234F786A64D05E78B4280D"
    for event in events:
      if event._type in self.interests:
        event.subscribe(self)

  def handle(self, event):
    if "steam" not in self.bot.mem_store:
      self._importpickle()

    steamapi.core.APIConnection(api_key=self.api_key)
    msg = event.line.split(":",2)[2]

    if msg.startswith(".steam set"):
      try: 
        self.bot.mem_store["steam"][msg.split()[2]] = msg.split()[3]
        pickle.dump(self.bot.mem_store["steam"], open("steamdict.p","w+b"))
      except IndexError:
        self.printer("PRIVMSG " +event.channel + " :Error! Need username to save under and steam ID number. \n")
        return

    if msg.startswith(".steam list"):
      for entry, key in self.bot.mem_store["steam"].items():
        self.printer("PRIVMSG " +event.channel + " :" + entry + " -- " + key + "\n")
      return

    if msg.startswith(".steam del"):
      try:
        del self.bot.mem_store["steam"][msg.split()[2]]
        return
      except KeyError:
        self.printer("PRIVMSG " +event.channel + " :No entry for " + msg.split()[2] + "\n")
        return

    if msg.startswith(".steam help"):
      self.printer("PRIVMSG " +event.channel + " :Set steam name to steamid with "  + "\n")
      self.printer("PRIVMSG " +event.channel + " :- .steam set <steamname> <steamid>"  + "\n")
      self.printer("PRIVMSG " +event.channel + " :Get friends with "  + "\n")
      self.printer("PRIVMSG " +event.channel + " :- .steam <username> friends"  + "\n")
      
    if msg.startswith(".steam friends"):
      try:
        user = steamapi.user.SteamUser(self.bot.mem_store["steam"][msg.split()[2]])
      except KeyError:
        self.printer("PRIVMSG " +event.channel + " :No entry for " + msg.split()[2] + "\n")
        return
      except IndexError:
        self.printer("PRIVMSG " +event.channel + " :Need steam username to print friends for. " + "\n")
        return

      self.bot.mem_store["steam"][user] = user.friends
      counter = 0
      line = ""
      players = list()
      for su in self.bot.mem_store["steam"][user]:
        if su.currently_playing is not None:
          players.append(su.name + " -- " + su.currently_playing.name)
          counter = counter + 1
      if counter is 0:
        self.printer("PRIVMSG " +event.channel + " :No friends in game."  + "\n")
      elif counter > 0:
        self.printer("PRIVMSG " +event.channel + " :" + ", ".join(players) + "\n")
 
  def _importpickle(self):
    try:
      self.bot.mem_store["steam"] = pickle.load(open("steamdict.p","rb"))
    except IOError, EOFError:
      self.bot.mem_store["steam"] = dict()
