from event import Event
import json
import requests

class Forecast:
    def __init__(self, events=None, printer_handle=None, bot=None):
        self.events = events
        self.printer = printer_handle
        self.interests = ['__.forecast__']
        self.bot = bot

        self.help = ".forecast <location>" 

        # register ourself for any events that we're interested in that exist already
        for event in events:
            if event._type in self.interests:
                event.subscribe(self)

    def get_location(self, location_search):
        """Returns a list of 3 items. A formatted location, a its latitude, and its longitude"""
        if location_search == '':
            return None
        address = location_search.replace(' ', '+')
        key = "AIzaSyA95TSuDZMUySAeijsNuIiqX7cJFbXKUSw" 
        parameters = {'address': address, 'sensor': 'false', 'key': key}
        try:
            geocode = requests.get('https://maps.googleapis.com/maps/api/geocode/json', params=parameters).json()
        except:
            return None 
        latitude = geocode['results'][0]['geometry']['location']['lat']
        longitude = geocode['results'][0]['geometry']['location']['lng']
        location_name = geocode['results'][0]['formatted_address']
        return [location_name, str(latitude), str(longitude)]

    def get_forecast(self, latitude="", longitude=""):
        """Returns a JSON formatted object with all weather data on the requested 
        latitude and longitude. latitude and longitude are strings
        """
        key = "5a9290d413a126311a547f2de4f510c6"
        try:
            return requests.get('https://api.forecast.io/forecast/'+key+'/'+latitude+','+longitude).json()
        except ValueError:
            return {}

    def current(self, current_data={}):
        """Takes a JSON formatted object of data on current weather conditions from forecast.io
        Formats into a summarized string for IRC bot use
        """
        #if no data provided, return a string saying so
        conditions = ''
        if current_data == {}:
            return "No data on current weather conditions."
        conditions += str(round(current_data['temperature'])) + u'\u00B0.'
        if current_data['cloudCover'] >= 0 and current_data['cloudCover'] < 0.4:
            conditions += " Clear skies."
        elif current_data['cloudCover'] >= 0.4 and current_data['cloudCover'] < 0.75:
            conditions += " Partly cloudy."
        elif current_data['cloudCover'] >= 0.75 and current_data['cloudCover'] < 1: 
            conditions += " Mostly cloudy."
        else:
            conditions += " Overcast."

        try:
            if current_data['precipIntensity'] > 0:
                if current_data['precipIntensity'] > 0 and current_data['precipIntensity'] <= 0.017:
                    conditions += " Very light "
                elif current_data['precipIntensity'] > 0.017 and current_data['precipIntensity'] <= 0.1:
                    conditions += " Light "
                elif current_data['precipIntensity'] >= 0.1 and current_data['precipIntensity'] < 0.4:
                    conditions += " Moderate "
                elif current_data['precipIntensity'] >= 0.4:
                    conditions += " Heavy "
                conditions += current_data['precipType'] + '.'
        except KeyError:
            pass
        return conditions

    def handle(self, event):
        _z = str.split(event.msg, None, 1)
        if _z[1] != '':
            #cur = _z[-1]
            loc = self.get_location(_z[1])
            cur = self.current(self.get_forecast(loc[1], loc[2])['currently'])
            try:
                self.printer("PRIVMSG " + event.channel + ' :' + loc[0] + ': ' +  cur + '\n')
            except TypeError:
                print "DEBUG: TypeError: ",
                print event.channel,
                print event.user
