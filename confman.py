import os
import json
from conferror import ConfError
class ConfManager:

  def __init__(self,conf=None):
    if conf is not None:
      try:
        self.conf_file = open(os.path.abspath(conf))
      except IOError:
        raise ConfError("could not open conf file '"+conf+"'")
    if conf is None:
      if os.environ.has_key('HOME'):
        try:
          self.conf_path = os.environ['HOME'] + '/.pybotrc'
          self.conf_file = open(self.conf_path)
        except IOError:
          raise ConfError("could not open conf file '"+self.conf_path+"'")
      else: # lines of with os.environ.has_key
        try:
          self.conf_file = open('.pybotrc')
        except IOError:
          self.conf_path = os.environ['HOME'] + '/.pybotrc'
          try:
            #self.conf_path = os.environ['HOME'] + conf
            self.conf_file = open(self.conf_path)
          except IOError:
            raise ConfError("could not open conf file '"+self.conf_path+"'")
    
    self.parsed = json.load(self.conf_file)

  def getOwner(self, net):
    return self.parsed[net]["owner"]

  def getIRCPass(self, net):
    return self.parsed[net]["ircpass"]

  def getDBPass(self, net):
    return self.parsed[net]["dbpass"]

  def getNumChannels(self, net):
    return len(self.parsed[net]["channels"])

  def getNick(self, net):
    return self.parsed[net]["nick"]

  def getChannels(self, net):
    return self.parsed[net]["channels"]

  def getNetworks(self):
    l = list()
    for n in self.parsed.iterkeys():
      l.append(n)
    return l
  
  def getNumNets(self):
    i = 0
    for n in self.parsed.iterkeys():
      i += 1
    return i

# deprecated
  def getNetwork(self):
    pass

  def getPort(self,net):
    return self.parsed[net]["port"]
