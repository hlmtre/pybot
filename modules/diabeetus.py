# -*- coding: utf-8 -*-

import requests
import re
import json
import sys
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

class Diabeetus(BaseModule):

    def post_init(self):
        diabeetus = Event('__.diabeetus__')
        diabeetus.define(msg_definition='^\.[Dd]iabeetus')
        diabeetus.subscribe(self)
        self.bot.register_event(diabeetus, self)
        self.api_url = "https://bonkscout.herokuapp.com/api/v1/entries/current.json"
        self.LOW = 69
        self.HIGH = 200
        self.trend = {
            "Flat": "→",
            "FortyFiveDown":"↘",
            "FortyFiveUp":"↗",
            "SingleDown":"↓",
            "SingleUp":"↑",
            "DoubleDown":"⇊",
            "DoubleUp":"⇈",
            "TripleDown":"⇓",
            "TripleUp":"⇑"
        }

    def get_glucose(self, channel):
        """get the glucose"""
        r = requests.get(self.api_url)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self.say(channel, "Encountered an error contacting the NightScout API")
            return
        entry = r.json()
        try:
            #grab the relevant data we want for formatting
            glucose = entry[0]['sgv']
            if (glucose <= self.LOW):
                color = '\x0304'
            elif (glucose >= self.HIGH):
                color = '\x0308'
            else:
                color = '\x0303'
            arrow = self.trend[entry[0]['direction']]
            
        except KeyError:
            self.say(channel, "Unable to get glucose data from results. Sorry.")
            return
        #return the formatted string
        return "Bonk's blood sugar is " + color + str(glucose) + "\x0F mg/dL, trending " + arrow 

  
    def handle(self, event):
        self.say(event.channel, self.get_glucose(event.channel))
