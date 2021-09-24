## r6 created by mech ##
##  A simple progam to pull stats using r6tab ##

import sys
import json
from event import Event

try:
    from range_key_dict import RangeKeyDict
except (ImportError, SystemError):
    print("Warning: r6 module requires range_key_dict")
    range_key_dict = object

try:
    import requests
except (ImportError, SystemError):
    print("Warning: r6 module requires requests")
    requests = object

if sys.version_info > (3, 0, 0):
    try:
        from .basemodule import BaseModule
    except (ImportError, SystemError):
        from modules.basemodule import BaseModule
else:
    try:
        from basemodule import BaseModule
    except (ImportError, SystemError):
        from modules.basemodule import BaseModule

"""
For r6 module to work you need to create a file called 'r6_cred.py'
Format it like this:

class R6_Cred:
    api_key = "PuT ApI KeY Here"

"""
try:
    from modules.r6_cred import R6_Cred as rc
    key_check = True
except (ImportError, SystemError):
    print("Warning: r6 module requires API key in modules/r6_cred.py")
    key_check = False


class R6(BaseModule):
    """ Takes specified stats from r6tab and prints them to irc channel """

    def post_init(self):
        r6 = Event("__.r6__")
        r6.define(msg_definition=r"^\.r6")
        r6.subscribe(self)
        self.help = ".r6 <kd,level,rank> <gamer-tag>"
        # register ourself to our new r6 event
        self.bot.register_event(r6, self)
        self.player_ids = []
        self.url = "https://r6.apitab.com/search/uplay/"  # URL which outputs JSON data
        self.ranks = RangeKeyDict({
            (0, 1199): "Copper V",
            (1200, 1299): "Copper IV",
            (1300, 1399): "Copper III",
            (1400, 1499): "Copper II",
            (1500, 1599): "Copper I",
            (1600, 1699): "Bronze V",
            (1700, 1799): "Bronze IV",
            (1800, 1899): "Bronze III",
            (1900, 1999): "Bronze II",
            (2000, 2099): "Bronze I",
            (2100, 2199): "Silver V",
            (2200, 2299): "Silver IV",
            (2300, 2399): "Silver III",
            (2400, 2499): "Silver II",
            (2500, 2599): "Silver I",
            (2600, 2799): "Gold III",
            (2800, 2999): "Gold II",
            (3000, 3199): "Gold I",
            (3200, 3599): "Platinum III",
            (3600, 3999): "Platinum II",
            (4000, 4399): "Platinum I",
            (4400, 4999): "Diamond",
            (5000, 9999): "Champions"
        })

# Deals with presenting data that has been requested
    def print_stats(self, ids, js, choice):
        level = str(js['players'][ids]['stats']['level'])
        kd = str(js['players'][ids]['ranked']['kd'])
        rank = str(js['players'][ids]['ranked']['mmr'])
        if choice == "rank":
            return rank + " | " + self.ranks[int(rank)]
        elif choice == "kd":
            return kd
        elif choice == "level":
            return level

# Retrieves the JSON data from the API
    def api_get(self, name):
        """Needed to set user agent so request would not be blocked, without this a 503 status code is returned"""
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        }
        # Takes our static URL and appends your site to the end to make our get
        # request
        r = requests.get(
            self.url +
            name +
            "?cid=" +
            rc.api_key,
            headers=headers)
        j = json.loads(r.text)  # Converts our JSON to python object
        return j

        """
    Example to show json data parameters that can be pulled from with current URL get request:

    level	107
    ranked
    kd	0.7
    mmr	1881
    rank	6
    champ	0
    NA_mmr	1881
    NA_rank	0
    NA_champ	0
    EU_mmr	0
    EU_rank	0
    EU_champ	0
    AS_mmr	0
    AS_rank	0
    AS_champ	0
    """

    def handle(self, event):
        if key_check == True:
            if len(event.msg.split()
                   ) == 3:  # Looks for the properly formatted command
                option = event.msg.split()[1]
                player = event.msg.split()[2]
                try:
                    for value in self.api_get(
                            player)['players']:  # Adds all player ID's to a list
                        p_id = value
                        self.player_ids.append(p_id)
                    if self.api_get(player)['foundmatch'] == True and len(
                            self.player_ids) == 1:  # If only one match is found, print the requested data
                        self.print_stats(
                            self.player_ids[0], self.api_get(player), option)
                        self.say(
                            event.channel,
                            self.print_stats(
                                self.player_ids[0],
                                self.api_get(player),
                                option))
                        self.player_ids.clear()
                    # If no ids are found for requested player name tell the
                    # user
                    elif len(self.player_ids) == 0:
                        self.player_ids.clear()
                        self.say(event.channel, "No player found.")
                    else:  # If multiple options are found we compare against the requested player and the found ones.
                        for i in self.player_ids:
                            if player == self.api_get(player)[
                                    'players'][i]['profile']['p_name']:  # If exact player is found we print the data
                                self.print_stats(
                                    i, self.api_get(player), option)
                                self.say(
                                    event.channel, self.print_stats(
                                        self.player_ids[0], self.api_get(player), option))
                                self.player_ids.clear()
                            # If not at end of list keep looping and comparing
                            elif self.player_ids.index(i) < len(self.player_ids) - 1:
                                print(self.player_ids.index(
                                    i) + len(self.player_ids))
                                continue
                            else:  # If we run out of players to compare against then he does not exist and we let the user know
                                self.say(event.channel, "No player found.")
                        self.player_ids.clear()

                except requests.ConnectionError:
                    self.say(event.channel, "Connection error.")
        else:
            self.say(
                event.channel,
                "No API key found. Put in request at https://tabstats.com/contact")
