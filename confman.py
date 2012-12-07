import os
import conferror
class ConfManager:
	def __init__(self):
		if os.environ.has_key('HOME'):
			self.conf_path = os.environ['HOME'] + '/.pybotrc'
			self.conf_file = open(self.conf_path)
		else:
			raise ConfError("conf file not found")

		for line in self.conf_file:
			if line.startswith("owner"):
				self.owner = line.rstrip().split()[-1] # owner = username
			elif line.startswith("ircpass"):
				self.ircpass = line.rstrip().split()[-1] # ircpass = pass
			elif line.startswith("dbpass"):
				self.dbpass = line.rstrip().split()[-1] # dbpass = pass
