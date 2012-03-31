# -*- coding: UTF-8 -*-
#
# Copyright (c) 2012 Harry Gabriel <h.gabriel@nodefab.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import urllib
import time
import base64
import hashlib
import hmac

try:
    # python version 2.6 or newer
    import json
except ImportError:
    try:
        # older python versions
        import simplejson as json
    except ImportError:
        # Houston, we have a problem
        raise ImportError, 'Unable to load a json library'

class API(object):
    """A python interface for the bf3stats.com API"""

    def __init__(self, base_url=None, plattform='pc', secret=None, ident=None):

        # setup url to bf3stats.com API
        if base_url is None:
            self._base_url = 'http://api.bf3stats.com'
        else:
            self._base_url = base_url
        # can be pc, 360 or ps3
        self._plattform = plattform
        # ident and secret for signed requests
        if ident:
            self._ident = ident
        if secret:
            self._secret = secret

    def _request(self, post_data, data_group, sign=False, plattform=None):
        """Access bfstats.com API via HTTP POST"""
        # build url for current request
        if plattform is None:
            plattform = self._plattform
        api_url = '%s/%s/%s/' % (self._base_url, plattform, data_group)
        # sign data if we need
        if sign:
            post_data = self._sign(post_data)

        try:
            con = urllib.urlopen(api_url, urllib.urlencode(post_data))
            result = con.read()
            con.close()
            raw_data = json.loads(result)
        except IOError, err:
            raw_data = {'status' : 'error', 'error': err}
        return objDict(raw_data)

    def _sign(self, data_dict):
        """Sign data for a signed request"""
        data = base64.urlsafe_b64encode(json.dumps(data_dict)).rstrip('=')
        sig = base64.urlsafe_b64encode(
                hmac.new(self._secret, msg=data, digestmod=hashlib.sha256).digest()
                ).rstrip('=')
        return { 'data': data, 'sig': sig }

    # reimplement bf3stats.com JSON API
    # Method names taken from the documentation
    # http://bf3stats.com/api_url
    def playerlist(self, players):
        """Request a list of players"""
        pass

    def player(self, player_name, platform, parts=None):
        """Request a player"""
        post_data = {
                'player' : player_name,
                'opt' : parts
                }
        return self._request(post_data, 'player', False, platform)

    def dogtags(self, player_name):
        """Request Player dogtags"""
        return self._request(post_data = {'player': player_name}, data_group='dogtags')

    def onlinestats(self):
        """Count of online players"""
        return  self._request(post_data={}, data_group='onlinestats', plattform='global')


    def playerupdate(self, player_name, data_group='playerupdate'):
        """Request a playerupdate. (signed request)

        bf3stats.com request the current data from EA for this player.
        If the player was not in bf3stats.com database, they do automatically a lookup and add the player.

        Note: Clock should not have more than 1 minute difference to current time.
        """
        post_data = {
                'ident': self._ident,
                'time': int(time.time()),
                'player': player_name
                }
        return self._request(post_data, data_group, sign=True)

    def playerlookup(self, player_name):
        """Lookup a player. (signed request)"""
        # the code would be the same as playerupdate - let reuse this function
        return self.playerupdate(player_name, data_group='playerlookup')

    def setupkey(self, client_ident, name):
        """Generate an individual client key for every installation"""
        post_data = {
                'ident': self._ident,
                'time': int(time.time()),
                'clientident': client_ident,
                'name': name
                }
        return self._request(post_data, data_group='setupkey', plattform='global', sign=True)

    def getkey(self, client_ident):
        """"Get information about a existing client key or your own key."""
        post_data = {
                'ident': self._ident,
                'time': int(time.time()),
                'clientident': client_ident,
                }
        return self._request(post_data, data_group='getkey', plattform='global', sign=True)


class objDict(object):
    '''The recursive class for building and representing objects with.'''
    # http://stackoverflow.com/questions/1305532/convert-python-dict-to-object

    def __init__(self, obj):
        for k, v in obj.iteritems():
            if isinstance(v, dict):
                setattr(self, _to_str(k).title(), objDict(v))
            else:
                setattr(self, k, v)

    def __getitem__(self, val):
        return self.__dict__[val]

    def __repr__(self):
        return '{%s}' % str(', '.join('%s : %s' % (k, repr(v)) for (k, v) in self.__dict__.iteritems()))

		
def _to_str(name):
    """Add _ if given string is a digit."""
    if name.isdigit():
        name = '_%s' % name

    return name