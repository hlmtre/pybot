import json
import requests


class Bing:
    # from modules.bing_credentials import BingCredentials as bc
    try:
        from modules.bing_credentials import BingCredentials as bc
    except (ImportError, SystemError):
        print(
            "Warning: bing module requires credentials in modules/bing_credentials.py")

        class PhonyBc:
            subscription_key = "None"

        bc = PhonyBc()
    # bing_api_url = "http://dev.virtualearth.net/REST/v1/Locations?query="
    # bing_api_key_string = "&key=AuEaLSdFYvXwY4u1FnyP-f9l5u5Ul9AUA_U1F-eJ-8O_Fo9Cngl95z6UL0Lr5Nmx"
    bing_api_key_string = bc.subscription_key
    bing_api_url = "https://atlas.microsoft.com/search/address/json?&subscription-key=" + bing_api_key_string + "&api-version=1.0&language=en-US&query="
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    }

    def get_lat_long_from_bing(self, location):
        """
        go grab the latitude/longitude from bing's really excellent location API.
        Returns: tuple of x,y coordinates - (0,0) on error
        """
        u = self.bing_api_url + location
        # print(u)
        j = json.loads(requests.get(u, self.headers).text)
        # print(json.dumps(j, indent=2))

        try:
            x = j['results'][0]['position']['lat']
            y = j['results'][0]['position']['lon']
        except IndexError:
            return (0, 0)
        return (x, y)
