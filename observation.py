#!/usr/bin/env python

import json

# Defined ranges that observations can fall into, If an 
# observation falls outside of this range it will be set to 0
MIN_TEMP
MAX_TEMP

MIN_PRESSURE
MAX_PRESSURE

MIN_HUMIDITY = 0
MAX_HUMIDITY = 100

MIN_LUX = 0
MAX_LUX = 40000

MIN_ALTITUDE = 0
MAX_ALTITUDE = 10000

class WeatherObservation:
    """
        Represents a weather object with Temperature, Barametric Pressure,
        Relative Humidity, Lux, Altitude.
    """

    # Valid weather types
    OBSERVATION_TYPE = ["temp", "pres", "rhum", "lux", "alt", "time"]

    def __init__(self, _obs):
        self.observation = dict()

        for key in self.OBSERVATION_TYPE:
            self.observation[key] = 0

        self.setObservation(_obs)

    def getObservation(self):
        return self.observation

    def setObservation(self, _obs):
        # TODO: Add bounds checking for each observation_type

        if type(_obs) == tuple:
            _dict = dict()
            _dict["temp"] = _obs[0]
            _dict["pres"] = _obs[1]
            _dict["rhum"] = _obs[2]
            _dict["lux"] = _obs[3]
            _dict["alt"] = _obs[4]
            _dict["time"] = _obs[5]
    
            _obs = _dict

        if type(_obs) == dict:
            for key, value in _obs.iteritems():
                if( key in self.OBSERVATION_TYPE ):
                    self.observation[key] = value
                else:
                    return False, "Invalid key" 
        else:
            return False, "Unknown format"    
