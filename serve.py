from bottle import route, run, template, HTTPError

@route("/api/")
def index():
    return '<h3>Available API paths:</h3><p>/api/weather/<type></p><p>types are: temp, pres, rhum, lux, alt</p>'

@route("/api/weather/<type>")
def weather(type):
    types = ["TEMP", "PRES", "RHUM", "LUX", "ALT"]

    if( type.upper() not in types ):
        raise HTTPError(404, "Invalid weather type: {}".format(type)) 
    
    
    
    return '<h3>{}</h3>'.format(type)



run(host='0.0.0.0', port=8080)
