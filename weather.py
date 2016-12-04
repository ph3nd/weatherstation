#!/usr/bin/env python

from datetime import datetime as dt
import os
import sqlite3

from observation import WeatherObservation

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

    # SQL statements
    CREATE_TABLE_OBSERVATIONS = '''CREATE TABLE observations
                (temperature real, preasure real, relative_humiditiy integer, lux real,
                 altitude integer, timestamp integer)'''
    SELECT_ALL = "SELECT * FROM observations ORDER BY timestamp DESC;"
    SELECT_LATEST = "SELECT * FROM observations ORDER BY timestamp DESC LIMIT 1;"
    SELECT_TIMESTAMP = "SELECT * FROM observations WHERE timestamp > {} ORDER BY timestamp DESC;"
    INSERT_OBSERVATION = "INSERT INTO observations VALUES({}, {}, {}, {}, {}, {});"

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

            c.execute(self.CREATE_TABLE_OBSERVATIONS)
            conn.commit()

            return conn, c

    def LoadObservations(self):
        # Read historical observations from database
        history = self._ReadDB(self.SELECT_ALL)
        
        print "WeatherHistory: {} records loaded.".format(len(history))
        observations = list()
        for obs in history:
            observations.append(WeatherObservation(obs).getObservation())

        return observations

    def AddObservation(self, _obs):
        wObs = WeatherObservation(_obs).getObservation()
        
        # Add observation values to the sql statement
        rtn = self._WriteDB(self.INSERT_OBSERVATION.format(wObs["temp"], wObs["pres"], wObs["rhum"], 
                wObs["lux"], wObs["alt"], wObs["time"]))

        if not rtn:
            raise Exception(rtn)

    def LatestObservation(self):
        return WeatherObservation(self._ReadDB(self.SELECT_LATEST)[0]).getObservation()
