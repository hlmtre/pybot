import MySQLdb as mdb
from datetime import datetime,timedelta
class DB:
	age = datetime.now()

	def _open(self):
		self.con = mdb.connect("localhost","pybot","1q2w3e4r","pybot")
		self.cur = con.cursor()
	
	def _close(self):
		self.con = None
		self.cur.close()

	# should prevent mysql has gone away errors.. ideally
	def _handle(self):
		global cur
		global age
		now = datetime.now()
		if now - self.age > timedelta(minutes=5):
			self.cur.close()
			self.con = mdb.connect("localhost","pybot","1q2w3e4r","pybot")
			self.cur = self.con.cursor()

	def insert(self, where, which, what):
		self.cur.execute("""INSERT INTO %s (%s) VALUES (%s)""",(where, which, what)) 

	def updateSeen(self,who,statement,event):
		self._open()
		#print "executing REPLACE INTO seen (user_name, statement, event) VALUES ( " + str(who) + " " + str(statement) + " " + str(event) + ")"
		self.cur.execute("REPLACE INTO seen (user_name, statement, event) VALUES (%s, %s, %s)", (who, statement, event))
		self._close()

	def getSeen(self, who):
		self._open()
		if who != "":
			self.cur.execute("SELECT user_name, date, statement, event FROM seen WHERE user_name = %s", who)
			data = self.cur.fetchone()
			return data;
			self._close()
		else:
			self._close()
			return None 

	def _insertImg(self, user, url):
		self._open()
		if user == "" or user == None:
			user = "nobody"
		try:
			self.cur.execute("""INSERT INTO img (user, url) VALUES (%s, %s)""", (user, url))
			self.con.commit()
		except:
			self.con.rollback()

		self._close()

	def _getImgs(self):
		self._open()
		try:
			self.cur.execute("""SELECT * FROM img ORDER BY time""")
			data = self.cur.fetchall()
			self._close()
		except:
			self._close()
			return None

		return data

	def _isAdmin(self, username):
		self._open()
		try:
			self.cur.execute("""SELECT * FROM admins WHERE username = %s""",(username))
			data = self.cur.fetchall()
			self._close()
		except:
			self._close()
			return None

		return data
