import MySQLdb as mdb
from datetime import datetime,timedelta
class DB:
  age = datetime.now()

  def _open(self):
    self.con = mdb.connect("localhost","pybot","1q2w3e4r","pybot")
    self.cur = self.con.cursor()
  
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

  def select(self, where, what):
    try:
      self._open()
      self.cur.execute("""SELECT %s FROM %s""")
      data = self.cur.fetchall()
      self._close()
    except:
      self._close()
      return None

    return data

  def replace(self, where, which, what):
    try:
      self._open()
      self.cur.execute("""REPLACE INTO %s (%s) VALUES (%s)""",(where, which, what)) 
      self._close()
    except:
      self._close()
      return None

  def e(self, sql):
    try:
      self._open()
      self.cur.execute(sql) 
      if "INSERT" in sql:
        self.con.commit()
        self._close()
      elif "SELECT" in sql:
        e = self.cur.fetchall()
        self._close()
        return e
    except Exception, e:
      print e
      self.con.rollback()
      self._close()
      return None

  def insert(self, where, which, what):
    try:
      self._open()
      self.cur.execute("""INSERT INTO %s (%s) VALUES (%s)""",(where, which, what)) 
      self._close()
    except:
      self._close()
      return None

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
