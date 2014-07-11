import urllib2
import json

class Weather:
  def __init__(self, events=None, printer_handle=None, bot=None, say=None):
    self.events = events
    self.printer = printer_handle
    self.interests = ['__.weather__']
    self.bot = bot
    self.say = say

    self.help = ".weather <zipcode>, .weather <city> <state>"

    for event in events:
      if event._type in self.interests:
    #    print "DEBUG: registering to ",
    #    print event
        event.subscribe(self)

  def handle(self, event):
    _z = event.line.split()
    if _z[-1] != "":
      #print event.msg.split()[1:]
      try:
        # for specifying by name
        if len(event.msg.split()[1:]) > 1: # looking for .weather san francisco ca
          autocomplete_url = 'http://autocomplete.wunderground.com/aq?query=' + " " .join(event.msg.split()[1:]) # should be everything after weather
          response = urllib2.urlopen(autocomplete_url)
          try:
            j = response.read()
          except urllib2.HTTPError:
            self.printer("PRIVMSG " + event.channel + " :Wunderground appears down. Sorry\n")
            return

          parsed = json.loads(j)
          try:
            zipcode = parsed['RESULTS'][0]['zmw']
          except IndexError:
            return
          url = 'http://api.wunderground.com/api/1fe31b3b4cfdab66/conditions/lang:EN/q/'+zipcode[:5]+'.json'

        # by zipcode
        else:
          zipcode = _z[-1] # zipcode should be last word on line (.weather 95928, eg)
          url = 'http://api.wunderground.com/api/1fe31b3b4cfdab66/conditions/lang:EN/q/'+zipcode+'.json'

        try:
          response = urllib2.urlopen(url)
        # catch timeouts
        except urllib2.HTTPError:
          self.printer("PRIVMSG " + event.channel + " :Wunderground appears down. Sorry\n")
          return

        json_string = response.read()
        parsed_json = json.loads(json_string)
        #print json_string
        self.printer("PRIVMSG " + event.channel + " :" + parsed_json['current_observation']['display_location']['city'] + ", " + parsed_json['current_observation']['display_location']['state'] + ": " + parsed_json['current_observation']['weather'] + ", " + parsed_json['current_observation']['feelslike_string'] + ", " + parsed_json['current_observation']['relative_humidity'] +" humidity"+ '\n')
        #self.printer("PRIVMSG " + event.channel + " :For complete info: http://www.wunderground.com/cgi-bin/findweather/hdfForecast?query="+zipcode + '\n')
      except KeyError, e:
        pass
