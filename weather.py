#!/usr/bin/env python

from datetime import datetime as dt
import sqlite3

class WeatherPoint:
    """
        Represents a weather object with Temperature, Barametric Pressure,
        Relative Humidity, Lux, Altitude.
    """

    # Valid weather types
    WEATHER_TYPES = ["temp", "pres", "rhum", "lux", "alt"]

    def __init__(self, _weather, _timestamp):
        self.weather = dict()
        self.timestamp = timestamp        

        for type in WEATHER_TYPES:
            self.weather[type] = 0

    def getWeather(self):
        return self.weather

    def setWeather(self, _weather)
        
        for key, value in _weather:
            if( key in WEATHER_TYPES ):
                self.weather[key] = value
            else:
                return False

    def setTimestamp(self, _timestamp)
        self.timestamp = _timestamp

    def getTimestamp(self)
        return self.timestamp



class Weather:
    """
        Represents all historical data stored in the database,
        includes helper functions to save and retrieve from sqlite
        and includes function to feed the weather API found in serve.py
        to be used for front end display to users.
    """

    DBFILE = "Weather.db"

    def __init__(self, _dbfile):
        if( _dbfile ):
            self.dbfile = _dbfile
        else:
            self.dbfile = DBFILE
        
        # Init our DB
        self.conn = sqlite3.connect(self.dbfile)


    def WriteDB(self, sql)
        pass

    def ReadDB(self, sql)
        pass


    
