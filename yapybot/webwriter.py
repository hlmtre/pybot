import os
class WebWriter:
  """
  Handles writing out to teh home folder of the running user.
  Creates a very simple web page that just lists all the images posted in a channel the bot's in.
  Probably in trouble for cp because of teh 4cdn links.
  """
  def __init__(self):
    self.path = '~/public_html/img/'

  def _generate(self, data):
    if data is None:
      return

    if not os.path.exists(os.path.expanduser(self.path)):
      os.makedirs(os.path.expanduser(self.path))

    with open(os.path.expanduser('~/public_html/img/index.html'),'w+') as f:
      f.write("<html><body>\n")
      f.write("<font size=7>ANYTHING AND EVERYTHING ON THIS PAGE MAY BE NSFW. YOU HAVE BEEN WARNED.</font><br />\n")
      for line in data:
        f.write(line[2] + " pasted link <a href=\"" + line[1] + "\">" + line[1] + "</a> at "+str(line[3])+" UTC<br>\n")
        f.write("</html></body>\n")
