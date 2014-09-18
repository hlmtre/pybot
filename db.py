import MySQLdb as mdb
from datetime import datetime,timedelta
class DB:
  """
  Handles connecting to the database and reading and writing data.
  Currently supports only MySQL/mariadb, and that probably needs to change.
  """
  age = datetime.now()

  def __init__(self, bot=None):
    self.bot = bot
    self.dry_run = False
    
  def _open(self):
    if self.bot is not None:
      dbusername = self.bot.conf.getDBUsername(self.bot.network)
      password = self.bot.conf.getDBPass(self.bot.network)
      dbname = self.bot.conf.getDBName(self.bot.network)
    else:
      dbusername = "pybot"
      password = "1q2w3e4r"
      dbname = "pybot"

    try:
      self.con = mdb.connect("localhost",dbusername,password,dbname)
    except mdb.OperationalError as e:
      self.dry_run = True
      print e
      return

    self.cur = self.con.cursor()
  
  def _close(self):
    self.con = None
    if not self.dry_run:
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
      if "INSERT" in sql or "REPLACE" in sql:
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

  def _insertImg(self, user, url, channel):
    self._open()
    if user == "" or user == None:
      user = "nobody"
    try:
      self.cur.execute("""INSERT INTO img (user, url, channel) VALUES (%s, %s, %s)""", (user, url, channel))
      if not self.dry_run:
        self.con.commit()
    except:
      if not self.dry_run:
        self.con.rollback()

    self._close()

  def _getImgs(self):
    self._open()
    try:
      self.cur.execute("""SELECT * FROM img ORDER BY time DESC""")
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
