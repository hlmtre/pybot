import os
from conferror import ConfError
class ConfManager:
	def __init__(self,conf=None):
		if conf is None:
			if os.environ.has_key('HOME'):
				try:
					self.conf_path = os.environ['HOME'] + '/.pybotrc'
					self.conf_file = open(self.conf_path)
				except IOError:
					raise ConfError("could not open conf file '"+self.conf_path+"'")
		else: # lines of with os.environ.has_key
			self.conf_path = os.environ['HOME'] + '/.pybotrc'
			try:
				#self.conf_path = os.environ['HOME'] + conf
				self.conf_file = open(self.conf_path)
			except IOError:
				raise ConfError("could not open conf file '"+self.conf_path+"'")

		for line in self.conf_file:
			if line.startswith("network"):
				if len(line.split("=")[-1].split()) > 1: # more than one entry
					self.networks = line.split("=")[-1].split() # create list
				else:
					self.networks = line.rstrip().split()[-1] # singular network; make this a string

			elif line.startswith("port"):
				self.port = line.rstrip().split()[-1] # port = 6667

			elif line.startswith("owner"):
				self.owner = line.rstrip().split()[-1] # owner = username

			elif line.startswith("ircpass"):
				self.ircpass = line.rstrip().split()[-1] # ircpass = pass

			elif line.startswith("dbpass"):
				self.dbpass = line.rstrip().split()[-1] # dbpass = pass

			elif line.startswith("channels"): # channels = chan1 chan2 chan3
				c = line.rstrip().split("=")[-1]
				self.channels = c.split()

		if self.networks is None or self.port is None or self.channels is None:
				raise ConfError("conf file incorrect")

	def getOwner(self):
		return self.owner

	def getIRCPass(self):
		return self.ircpass

	def getDBPass(self):
		return self.dbpass

	def getChannels(self):
		return self.channels

	def getNetworks(self):
		return self.networks
	
	def getNumNets(self):
		if type(self.networks) is str:
			return 1
		else:
			return len(self.networks)

	def getNetwork(self):
		return self.networks

	def getPort(self):
		return self.port
