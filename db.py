import MySQLdb as mdb
from datetime import datetime,timedelta
class DB:
	age = datetime.now()
	con = mdb.connect("localhost","pybot","1q2w3e4r","pybot")
	cur = con.cursor()

	# should prevent mysql has gone away errors.. ideally
	def _handle(self):
		global cur
		global age
		now = datetime.now()
		if now - self.age > timedelta(minutes=5):
			print "getting new mysql handle"
			self.cur.close()
			self.con = mdb.connect("localhost","pybot","1q2w3e4r","pybot")
			self.cur = self.con.cursor()

	def insert(self, where, which, what):
		global cur
		self.cur.execute("""INSERT INTO %s (%s) VALUES (%s)""",(where, which, what)) 

	def updateSeen(self,who,statement,event):
		self._handle()
		global cur
		#print "executing REPLACE INTO seen (user_name, statement, event) VALUES ( " + str(who) + " " + str(statement) + " " + str(event) + ")"
		self.cur.execute("REPLACE INTO seen (user_name, statement, event) VALUES (%s, %s, %s)", (who, statement, event))

	def getSeen(self, who):
		self._handle()
		global cur
		if who != "":
			self.cur.execute("SELECT user_name, date, statement, event FROM seen WHERE user_name = %s", who)
			data = self.cur.fetchone()
			return data;
		else:
			return None 

	def _insertImg(self, user, url):
		self._handle()
		global cur
		global con
		if user == "" or user == None:
			user = "nobody"
		try:
			self.cur.execute("""INSERT INTO img (user, url) VALUES (%s, %s)""", (user, url))
			self.con.commit()
		except:
			self.con.rollback()

	def _getImgs(self):
		self._handle()
		global cur
		global con
		try:
			self.cur.execute("""SELECT * FROM img ORDER BY time""")
			data = self.cur.fetchall()
		except:
			return None

		return data
