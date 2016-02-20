from event import Event
try:
  import twitter
except ImportError:
  twitter = object
try:
  from basemodule import BaseModule
except ImportError:
  from modules.basemodule import BaseModule

"""
  to use this, you'll need to create a file in the modules directory called 'twitter_credentials.py', and it should look like this:
    
    class PybotTwitter:
      api_key = "<your api key (sometimes called consumer key)>"
      api_secret = "<api/consumer secret>"

      access_token = "<your access token>"
      access_token_secret = "<access token secret>"

"""
class TwitterPoster(BaseModule):
  try:
    from modules.twitter_credentials import PybotTwitter as pt
  except ImportError:
    class PhonyPt:
      api_key = ""
      api_secret = ""
      access_token = ""
      access_token_secret = ""

    pt = PhonyPt()

  user_to_track = "bhhorg"

  def post_init(self):
    twitter = Event("__.twitter__")
    twitter.define(user_definition=self.user_to_track)
    twitter.subscribe(self)
    self.bot.register_event(twitter, self)

    twitter_command = Event("__.twitter_command__")
    twitter_command.define(msg_definition="^\.twitter url")
    twitter_command.subscribe(self)
    self.bot.register_event(twitter_command, self)
    
  def handle(self, event):
    if event._type == "__.twitter__":
      pt = self.pt
      api = twitter.Api(consumer_key=pt.api_key, 
                        consumer_secret=pt.api_secret, 
                        access_token_key=pt.access_token, 
                        access_token_secret=pt.access_token_secret)
      try:
        status = api.PostUpdate(event.user + ": " + event.msg[:(140 - (len(event.user) + 2))]) # "username: <message>" all must be <= 140 char
      except Exception as e:
        print e
        print len(event.msg[:(140 - len(event.user) + 2)])
    elif event._type == "__.twitter_command__":
      self.say(event.channel, "https://twitter.com/pybot_posts_irc")
