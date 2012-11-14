import MySQLdb as mdb
class DB:
	con = mdb.connect("localhost","pybot","1q2w3e4r","pybot")
	cur = con.cursor()

	def insert(self, where, which, what):
		global cur
		self.cur.execute("""INSERT INTO %s (%s) VALUES (%s)""",(where, which, what)) 

	def updateSeen(self,who,statement,event):
		global cur
		#print "executing REPLACE INTO seen (user_name, statement, event) VALUES ( " + str(who) + " " + str(statement) + " " + str(event) + ")"
		self.cur.execute("REPLACE INTO seen (user_name, statement, event) VALUES (%s, %s, %s)", (who, statement, event))

	def getSeen(self, who):
		global cur
		if who != "":
			self.cur.execute("SELECT user_name, date, statement, event FROM seen WHERE user_name = %s", who)
			data = self.cur.fetchone()
			return data;
		else:
			return None 
	
	
