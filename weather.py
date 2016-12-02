#!/usr/bin/env python

from datetime import datetime as dt
import os
import sqlite3

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

        for key, value in _obs.iteritems():
            if( key in self.OBSERVATION_TYPE ):
                self.observation[key] = value
            else:
                return False


"""
    Database table structure:
    table observations:
        real temperature,
        real pressurem,
        int relative_humidity,
        real lux,
        int altitude,
        int timestamp,
"""

class WeatherHistory:
    """
        Represents all historical data stored in the database,
        includes helper functions to save and retrieve from sqlite
        and includes function to feed the weather API found in serve.py
        to be used for front end display to users.
    """

    DBFILE = "Weather.db"

    def __init__(self, _dbfile):
        if( _dbfile ):
            print "here"
            self.dbfile = _dbfile
        else:
            self.dbfile = self.DBFILE
        
        # Init our DB
        self.conn, self.cur = self._CreateDB(self.dbfile)

    def _WriteDB(self, sql):
        if sqlite3.complete_statement(sql):
            try:
                self.cur.execute(sql)
                self.conn.commit()
            except sqlite3.Error as e:
               return e.args[0]
            
            return True
        else:
            return "Invalid SQL" 

    def _ReadDB(self, sql):
        if not sql.upper().startswith("SELECT"):
            return "Not a SELECT statement" 
        if sqlite3.complete_statement(sql):
            try:
                self.cur.execute(sql)
                
                return self.cur.fetchall()
            except sqlite3.Error as e:
                return e.args[0]
        else:
            return "Invalid SQL" 

    def _CreateDB(self, _dbfile):
        if( os.path.isfile(_dbfile) ):
            conn = sqlite3.connect(_dbfile)
            c = conn.cursor()
            return conn, c
        else:
            # Create database and initialise the tables
            conn = sqlite3.connect(_dbfile)
            c = conn.cursor()

            c.execute('''CREATE TABLE observations
                (temperature real, preasure real, relative_humiditiy integer, lux real, 
                    altitude integer, timestamp integer)''')

            conn.commit()

            return conn, c

    def LoadObservations(self):
        # Read historical observations from database
        history = self._ReadDB("SELECT * FROM observations;")
        
        print "WeatherHistory: {} records loaded.".format(len(history))

    def AddObservation(self, _obs):
        wObs = WeatherObservation(_obs).getObservation()
        
        # Create sql statement
        sql = "INSERT INTO observations VALUES({}, {}, {}, {}, {}, {});".format(wObs["temp"], wObs["pres"], wObs["rhum"], 
                wObs["lux"], wObs["alt"], wObs["time"])
        rtn = self._WriteDB(sql)

        if not rtn:
            raise Exception(rtn)
