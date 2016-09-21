import requests

api_key = "1fe31b3b4cfdab66"
def api_request(location, channel, command="conditions"):
    """location is a search string after the .weather command. This function
    will determine whether it is a zip code or a named location and return an
    appropriate API call"""
    #note for future: if wanted, add further detection of conditions or forecast searching
    query = None
    try:
      # test if is a zipcode or a single city name
      a = float(location.split()[0])
      if a and len(location.split()[0]) < 5:
        return None
      zipcode = re.match('[0-9]{5}', location)
      query = '/q/'+zipcode.string
    except ValueError: # it's a city name (or broken encoding on numbers or something)
      #create autocomplete search
      q = requests.get('http://autocomplete.wunderground.com/aq', params={'query':location})
      try:
          q.raise_for_status()
      except requests.exceptions.HTTPError:
          return None
      results = q.json()
      try:
          #attempt to grab the 'l' field from the first result
          #assuming it exists, this field will be what we use to search the conditions api
          query = results['RESULTS'][0]['l']
      except (IndexError, KeyError):
          #in case there were no results, let channel know
          return None

    if query:
        #return the full URL of the query we want to make
        return 'http://api.wunderground.com/api/'+api_key+'/' + command + query+'.json'
    return None

def get_conditions(query, channel):
    """given a fully formed query to the wundeground API, format an output string"""
    r = requests.get(query)
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError:
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
        return
    #return the formatted string of weather data
    return location + ': ' + conditions + ', ' + temp_f + 'F (' + temp_c + 'C). Humidity: ' + humidity
