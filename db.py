import MySQLdb as mdb
class DB:
	con = mdb.connect("localhost","pybot","1q2w3e4r","pybot")
	cur = con.cursor()

	def insert(self, where, which, what):
		global cur
		self.cur.execute("""INSERT INTO %s (%s) VALUES (%s)""",(where, which, what)) 

	def updateSeen(self,who,statement):
		global cur
		self.cur.execute("REPLACE INTO seen (user_name, statement) VALUES (%s, %s)", (who, statement))

	def getSeen(self, who):
		global cur
		self.cur.execute("SELECT user_name, statement FROM seen WHERE user_name = %s", who)
		data = cur.fetchone()
		return data;
	
	def updateSeen(self,chanlist):
		global cur
		for chan in chanlist:
			print "got "+chan


	
