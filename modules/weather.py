# -*- coding: utf-8 -*-

import requests 
import re
import json
from event import Event
try:
    from .basemodule import BaseModule
except ImportError:
    from modules.basemodule import BaseModule

class Weather2(BaseModule):

    def post_init(self):
        weather2 = Event('__.weather2__')
        weather2.define(msg_definition='^\.[Ww]eather')
        weather2.subscribe(self)

        self.bot.register_event(weather2, self)
        # now using openweathermap as wunderground ended theirs :(
        self.api_key = "6dc001f4e77cc0985c5013283368be51"
        self.api_url = "https://api.openweathermap.org/data/2.5/weather"
    

    def api_request(self, location, channel, command="conditions"):
        """location is a search string after the .weather command. This function
        will determine whether it is a zip code or a named location and return an
        appropriate API call"""
        query = None
        try:
          # test if is a zipcode or a single city name
          a = float(location.split()[0])
          if a and len(location.split()[0]) < 5:
            self.say(channel,"valid zipcode required, numbnuts")
            return None
          zipcode = re.match('[0-9]{5}', location)
          query = '?zip='+zipcode.string
        except ValueError: #  broken encoding on numbers or something or they tried a city name
            self.say(channel, "city name no longer supported due to wunderground API shutdown :(")

        if query:
            return self.api_url+query+"&appid="+self.api_key+"&units=imperial"
        return None

    def get_conditions(self, query, channel):
        """given a fully formed query to the OpenWeatherMap API, format an output string"""
        r = requests.get(query)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self.say(channel, "Encountered an error contacting the OpenWeatherMap API")
            return
        weather = r.json()
        try:
            #grab the relevant data we want for formatting
            location = weather['name']
            conditions = weather['weather'][0]['main']
            temp_f = str(round(weather['main']['temp'], 1))
        except KeyError:
            self.say(channel, "Unable to get weather data from results. Sorry.")
            return
        #return the formatted string of weather data
        return location + ': ' + conditions + ', ' + temp_f + '° F' 

  
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
