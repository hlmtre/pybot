import requests 
import re
from event import Event
try:
    from basemodule import BaseModule
except ImportError:
    from modules.basemodule import BaseModule

class Weather2(BaseModule):

    def post_init(self):
        weather2 = Event('__.weather2__')
        weather2.define(msg_definition='^\.weather')
        weather2.subscribe(self)
        self.bot.register_event(weather2, self)
        self.api_key = "1fe31b3b4cfdab66"
    
    def api_request(self, location, channel):
        """location is a search string after the .weather command. This function
        will determine whether it is a zip code or a named location and return an
        appropriate API call"""
        #note for future: if wanted, add further detection of conditions or forecast searching
        query = None
        try:
          # test if is a zipcode or a single city name
          a = float(location.split()[0])
          if a and len(location.split()[0]) < 5:
            self.say(channel,"valid zipcode required, numbnuts")
            return None
          zipcode = re.match('[0-9]{5}', location)
          query = '/q/'+zipcode.string
        except ValueError: # it's a city name (or broken encoding on numbers or something)
          #create autocomplete search
          q = requests.get('http://autocomplete.wunderground.com/aq', params={'query':location})
          try:
              q.raise_for_status()
          except request.exceptions.HTTPError:
              self.say(channel, "Encountered an error contacting the WUnderground API")
              return None
          results = q.json()
          try:
              #attempt to grab the 'l' field from the first result
              #assuming it exists, this field will be what we use to search the conditions api
              query = results['RESULTS'][0]['l']
          except (IndexError, KeyError):
              #in case there were no results, let channel know
              self.say(channel, "No results found")
              return None

        if query:
            #return the full URL of the query we want to make
            return 'http://api.wunderground.com/api/'+self.api_key+'/conditions'+query+'.json'
        return None

    def get_conditions(self, query, channel):
        """given a fully formed query to the wundeground API, format an output string"""
        r = requests.get(query)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self.say(channel, "Encountered an error contacting the WUnderground API")
            return
        weather = r.json()
        try:
            #grab the relevant data we want for formatting
            location = weather['current_observation']['display_location']['full']
            conditions = weather['current_observation']['weather']
            temp_f = str(weather['current_observation']['temp_f'])
            temp_c = str(weather['current_observation']['temp_c'])
            humidity = weather['current_observation']['relative_humidity']
        except KeyError:
            self.say(channel, "Unable to get weather data from results. Sorry.")
            return
        #return the formatted string of weather data
        return location + ': ' + conditions + ', ' + temp_f + 'F (' + temp_c + 'C). Humidity: ' + humidity

  
    def handle(self, event):
        #split the line beginning with .weather into 2 parts, the command and the search string
        weather_line = event.msg.split(None, 1)
        if len(weather_line) > 1:
            #if we're sure there's actually a search string, then continue
            query = self.api_request(weather_line[1], event.channel)
            if not query:
                return
            weather = self.get_conditions(query, event.channel)
            if not weather:
                return
            self.say(event.channel, weather)
        else:
            #chastise the user for being silly and not actually searching for a location
            self.say(event.channel, "It would help if you supplied an actual location to search for.")
