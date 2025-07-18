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

try:
    from owm_api import Owm_Api as oa
except (ImportError, SystemError):
    print("Warning: weather module requires credentials in $PYBOT_ROOT/owm_api.py")

    class Phony_Owm_Api:
        api_key = "None"
    oa = Phony_Owm_Api()


class Weather(BaseModule):

    def post_init(self):
        weather2 = Event('__.weather2__')
        weather2.define(
            msg_definition=r'^\.weather |^\.w ',
            case_insensitive=True)
        weather2.subscribe(self)

        self.bot.register_event(weather2, self)
        # two apis because we get the lat/long from openmeteo
        self.meteo_api_url = "https://geocoding-api.open-meteo.com/v1/search?count=10&language=en&format=json&name="
        self.api_url = "https://api.openweathermap.org/data/2.5/weather"
        self.api_key = oa.api_key
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        }

    def get_lat_long_from_bing(self, location):
        """
        Returns: tuple of x,y coordinates - (0,0) on error
        """
        u = self.meteo_api_url + location
        # print(u)
        j = json.loads(requests.get(u, self.headers).text)
        # print(j['results'][0])

        try:
            x = j['results'][0]['latitude']
            y = j['results'][0]['longitude']
        except IndexError:
            return (0, 0)
        return (x, y)

    def get_api_request(self, x, y):
        """
        Simple form the query string and return it.
        """
        return self.api_url + "?lat=" + \
            str(x) + "&lon=" + str(y) + \
            "&units=imperial" + "&appid=" + self.api_key

    def get_conditions(self, query, channel):
        """given a fully formed query to the OpenWeatherMap API, format an output string"""
        r = requests.get(query)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self.say(
                channel,
                "Encountered an error contacting the OpenWeatherMap API")
            return
        weather = r.json()
        # print(weather)
        try:
            # grab the relevant data we want for formatting
            location = weather['name']
            conditions = weather['weather'][0]['main']

            if conditions == "Clear":
                icon = '\N{sun}'
            elif conditions == "Rain" or conditions == "Drizzle":
                icon = '\N{cloud with rain}'
            elif conditions == "Thunderstorm":
                icon = '\N{cloud with lightning}'
            elif conditions == "Clouds":
                icon = '\N{cloud}'
            elif conditions == "Snow":
                icon = '\N{cloud with snow}'
            elif conditions == "Mist":
                icon = '\N{fog}'
            else:
                icon = '\N{fire}'

            temp_f = round(weather['main']['temp'], 1)
            temp_c = round((temp_f - 32) * (5.0 / 9.0), 1)
            # sky = weather['weather'][0]['main']
            # print(sky)
        except KeyError:
            self.say(
                channel,
                "Unable to get weather data from results. Sorry.")
            return
        # return the formatted string of weather data
        # return location + ': ' + conditions + " 🌧️ " + ', ' + \
        return location + ': ' + conditions + ' ' + icon + ', ' + \
            str(temp_f) + '°F (' + str(temp_c) + '°C)'

    def handle(self, event):
        # split the line beginning with .weather into 2 parts, the command and
        # the search string
        weather_line = event.msg.split(None, 1)
        if len(weather_line) > 1:
            # if we're sure there's actually a search string, then continue
            x, y = self.get_lat_long_from_bing(weather_line[1])
            weather = self.get_conditions(
                self.get_api_request(
                    x, y), event.channel)
            if not weather:
                return
            self.say(event.channel, weather)
        else:
            # chastise the user for being silly and not actually searching for
            # a location
            self.say(
                event.channel,
                "It would help if you supplied an actual location to search for.")
