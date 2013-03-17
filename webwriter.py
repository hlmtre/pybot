from db import DB
class WebWriter:
	db = DB()
	def __init__(self):
		pass	

	def _generate(self):
		global db
		data = self.db._getImgs()
		f = open('/home/pybot/public_html/img/index.html','w')
		if data:
			f.write("<html><body>\n")
			f.write("<font size=7>ANYTHING AND EVERYTHING ON THIS PAGE MAY BE NSFW. YOU HAVE BEEN WARNED.</font><br />\n")
			for line in data:
				f.write(line[2] + " pasted link <a href=\"" + line[1] + "\">" + line[1] + " at "+line[3]+"</a><br>\n")

			f.write("</html></body>\n")
