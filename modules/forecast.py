from event import Event
import json
import requests

class Forecast:
    def __init__(self, events=None, printer_handle=None, bot=None, say=None):
        self.events = events
        self.printer = printer_handle
        self.interests = ['__.forecast__']
        self.bot = bot

        forecast = Event("__.forecast__")
        forecast.define(msg_definition="^\.forecast")
        forecast.subscribe(self)
        self.bot.register_event(forecast, self)

        self.help = ".forecast <location>" 

    def get_location(self, location_search):
        """Returns a list of 3 strings. A formatted location, its latitude, and its longitude"""
        if location_search == '':
            return None
        address = location_search.replace(' ', '+')
        key = 'AIzaSyBr4KECytQxPN8PDZhWczIvyK7voqjdN3c'
        #key = "AIzaSyA95TSuDZMUySAeijsNuIiqX7cJFbXKUSw" 
        parameters = {'address': address, 'sensor': 'false', 'key': key}
        try:
            raw = requests.get('https://maps.googleapis.com/maps/api/geocode/json', params=parameters)
            raw.raise_for_status()
            geocode = raw.json()
        except ValueError:
            return ['Error: Cannot form json object']
        except requests.exceptions.HTTPError:
            return ['Trouble retrieving data from Google API']
        try:
            latitude = geocode['results'][0]['geometry']['location']['lat']
            longitude = geocode['results'][0]['geometry']['location']['lng']
            location_name = geocode['results'][0]['formatted_address']
        except (IndexError, KeyError), e:
            return ['Location not found']
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
        #Add the data on current temperature. We round the data, cast as int, add into the string
        conditions += str(int(round(current_data['temperature']))) + u'\u00B0.'
        #Add data on cloud cover. Should alway be available. Descriptions taken from forecast.io api docs
        if current_data['cloudCover'] >= 0 and current_data['cloudCover'] < 0.4:
            conditions += " Clear skies."
        elif current_data['cloudCover'] >= 0.4 and current_data['cloudCover'] < 0.75:
            conditions += " Partly cloudy."
        elif current_data['cloudCover'] >= 0.75 and current_data['cloudCover'] < 1: 
            conditions += " Mostly cloudy."
        else:
            conditions += " Overcast."

        #If there is any precipitation data, get the intensity and type of precipitation added into the description
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
        #print "Debugging: Reached stage 1 of handle()"
        if _z[1] != '':
            cur = ''
            loc = self.get_location(_z[1])
            if len(loc) == 3: #if there are 3 items, valid data retrieved. if not, it didn't work
                cur = ': ' + self.current(self.get_forecast(loc[1], loc[2])['currently'])
            try:
                self.printer("PRIVMSG " + event.channel + ' :' + loc[0] + cur + '\n')
            except TypeError:
                print "DEBUG: TypeError: ",
                print event.channel,
                print event.user
