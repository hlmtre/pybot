import MySQLdb as mdb
class DB:
	con = mdb.connect("localhost","pybot","1q2w3e4r","pybot")
	cur = con.cursor()

	def insert(self, where, which, what):
		cur.execute("INSERT INTO %s (%s) VALUES (%s)",(where, which, what)) 


	
