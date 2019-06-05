#BOFH quote module created by hlmtre#
# depends on requests-html, which runs only on python 3
# perhaps TODO FIXME ?

from event import Event
import sys
try:
  from requests_html import HTMLSession
except (ImportError, SystemError):
  requests_html = None
import random
try:
  if sys.version_info > (3, 0, 0):
    from .basemodule import BaseModule
  else:
    import urlllib2 as urllib
    from basemodule import BaseModule
except (ImportError, SystemError):
  from modules.basemodule import BaseModule

class Bofh(BaseModule):
  def post_init(self):
    b_event = Event("__.bofh__")

    b_event.define(msg_definition="^\.bofh$")
    b_event.subscribe(self)

    self.bot.register_event(b_event, self)
    self.help = ".bofh (prints random quote)"
  def handle(self, event):
    try:
      if not requests_html:
        return
      session = HTMLSession()
      r = session.get('http://pages.cs.wisc.edu/~ballard/bofh/excuses')
      r_text = (r.text)
      r_list = r_text.split('\n')
      random_quote = random.randrange(0, len(r_list))
      self.say(event.channel, "BOFH: " + r_list[random_quote])
    except:
      pass
