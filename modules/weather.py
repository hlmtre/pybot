# -*- coding: utf-8 -*-

import json
import sys
import requests
from event import Event

if sys.version_info > (3, 0, 0):
    try:
        from .basemodule import BaseModule
    except (ImportError, SystemError):
        from modules.basemodule import BaseModule
else:
    try:
        from basemodule import BaseModule
    except (ImportError, SystemError):
        from modules.basemodule import BaseModule

class Weather(BaseModule):

    def post_init(self):
        weather2 = Event('__.weather2__')
        weather2.define(msg_definition='^\.[Ww]eather|^\.w')
        weather2.subscribe(self)

        self.bot.register_event(weather2, self)
        self.bing_api_url = "http://dev.virtualearth.net/REST/v1/Locations?query="
        self.bing_api_key_string = "&key=AuEaLSdFYvXwY4u1FnyP-f9l5u5Ul9AUA_U1F-eJ-8O_Fo9Cngl95z6UL0Lr5Nmx"
        self.api_key = "6dc001f4e77cc0985c5013283368be51"
        self.api_url = "https://api.openweathermap.org/data/2.5/weather"
        self.headers = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        }

    def get_lat_long_from_bing(self, location):
        """
        go grab the latitude/longitude from bing's really excellent location API.
        Returns: tuple of x,y coordinates - (0,0) on error
        """
        u = self.bing_api_url + location + self.bing_api_key_string
        j = json.loads(requests.get(u, self.headers).text)

        try:
            x = j['resourceSets'][0]['resources'][0]['geocodePoints'][0]['coordinates'][0]
            y = j['resourceSets'][0]['resources'][0]['geocodePoints'][0]['coordinates'][1]
        except IndexError:
            return (0, 0)
        return (x, y)

    def get_api_request(self, x, y):
        """
        Simple form the query string and return it.
        """
        return self.api_url + "?lat=" + str(x) + "&lon=" + str(y) + "&units=imperial" + "&appid=" + self.api_key

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
            temp_f = round(weather['main']['temp'], 1)
            temp_c = round((temp_f - 32) * (5.0/9.0))
        except KeyError:
            self.say(channel, "Unable to get weather data from results. Sorry.")
            return
        #return the formatted string of weather data
        return location + ': ' + conditions + ', ' + str(temp_f) + '°F (' + str(temp_c)  + '°C)'


    def handle(self, event):
        #split the line beginning with .weather into 2 parts, the command and the search string
        weather_line = event.msg.split(None, 1)
        if len(weather_line) > 1:
            ##if we're sure there's actually a search string, then continue
            x, y = self.get_lat_long_from_bing(weather_line[1])
            weather = self.get_conditions(self.get_api_request(x, y), event.channel)
            if not weather:
                return
            self.say(event.channel, weather)
        else:
            #chastise the user for being silly and not actually searching for a location
            self.say(event.channel, "It would help if you supplied an actual location to search for.")
