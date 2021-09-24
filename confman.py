import os
import json
from conferror import ConfError


class ConfManager:
    """
    Singleton class. Opens and parses a JSON-formatted conf file from (generally) the running user's home folder. Looks for .pybotrc.
    This allows each thread to know only its own network name, and always get back the information specified for that network from the confman.
    """

    def __init__(self, conf=None):
        if conf is not None:
            try:
                self.conf_file = open(os.path.expanduser(conf))
            except IOError:
                raise ConfError(
                    "could not open conf file '" +
                    os.path.expanduser(conf) +
                    "'")
        if conf is None:
            if 'HOME' in os.environ:
                try:
                    self.conf_path = os.environ['HOME'] + '/.pybotrc'
                    self.conf_file = open(self.conf_path)
                except IOError:
                    raise ConfError(
                        "could not open conf file '" + self.conf_path + "'")
            else:  # lines of with os.environ.has_key
                try:
                    self.conf_file = open('.pybotrc')
                except IOError:
                    self.conf_path = os.environ['HOME'] + '/.pybotrc'
                    try:
                        #self.conf_path = os.environ['HOME'] + conf
                        self.conf_file = open(self.conf_path)
                    except IOError:
                        raise ConfError(
                            "could not open conf file '" + self.conf_path + "'")

        self.parsed = json.load(self.conf_file)

    def getDBType(self):
        try:
            db_type = self.parsed["__pybot_conf"]["db_type"]
        except BaseException:
            return "mysql"

        return db_type

    def getOwner(self, net):
        return self.parsed[net]["owner"]

    def getTimeout(self, net):
        try:
            return int(self.parsed[net]["timeout"])
        except BaseException:
            return 120

    def getIRCPass(self, net):
        return self.parsed[net]["ircpass"]

    def getDBPass(self, net):
        return self.parsed[net]["dbpass"]

    def getDBName(self, net):
        return self.parsed[net]["dbname"]

    def getDBUsername(self, net):
        return self.parsed[net]["dbusername"]

    def getNumChannels(self, net):
        return len(self.parsed[net]["channels"])

    def getNick(self, net):
        return self.parsed[net]["nick"]

    def getChannels(self, net):
        return self.parsed[net]["channels"]

    def getNetworks(self):
        l = list()
        for n in list(self.parsed.keys()):
            if n != "__pybot_conf":
                l.append(n)
        return l

    def getNumNets(self):
        i = 0
        for n in list(self.parsed.keys()):
            if n != "__pybot_conf":
                i += 1
        return i

# deprecated
    def getNetwork(self):
        pass

    def getPort(self, net):
        return self.parsed[net]["port"]
