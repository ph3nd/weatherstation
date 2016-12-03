#!/usr/bin/env python

from bottle import route, run, template, HTTPError, redirect, default_app
from weather import WeatherHistory
import json


@route("/")
def index():
    redirect("/api/")    
    
@route("/api/")
def api():
    return '''
        <html><body>
        <h3>Available API paths:</h3>
        <p>GET /api/observation/&lt;type&gt; -  This returns a single datapoint for the most recent observation for any of these types values: temp, pres, rhum, lux, alt, time</p>
        <p>GET /api/observations - Returns all observations as a json object
        <p>GET /api/observations/&lt;timestamp&gt; - Returns all observations recorded since &lt;timestamp&gt;, which should be in unix time format.</p>
        <p>POST /api/addobservation - Adds a new observation based on the form data posted. Requires at least the timestamp to be provided values used are:. temp, pres, rhum, lux, alt, time</p>
        </body></html>
    '''

@route("/api/observation/<type>")
def observation(_type):
    types = ["TEMP", "PRES", "RHUM", "LUX", "ALT", "TIME"]

    if( _type.upper() not in types ):
        raise HTTPError(404, "Invalid observation type: {}".format(_type)) 
    
    return '{"{}":{}'.format(_type, )

@route("/api/observations")
def observations():
    wh = WeatherHistory(None)
    observations = wh.LoadObservations()

    return json.dumps(observations)

@route("/api/observations/<timestamp>")
def observations(timestamp):
    pass



app = application = default_app()
