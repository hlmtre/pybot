class Logger:
	def write(self, line):
		self.line = line
		f = open('logfile.txt', "a")
		f.write(self.line)
