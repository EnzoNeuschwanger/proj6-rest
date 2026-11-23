"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config

import pymongo # Database
import os      # For getting enviroment variables

import logging


###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY

client = pymongo.MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)
db = client.brevetdb
collection = db.brevetdb
collection.drop()

def calc_str_time(begin_date, time):
    year = int(begin_date.split("-")[0])
    month = int(time.split()[1].split('/')[0])
    day = int(time.split()[1].split('/')[1])
    hour = int(time.split()[2].split(':')[0])
    second = int(time.split()[2].split(':')[1])
    return arrow.get(year, month, day, hour, second)

###
# Pages
###

# No pages, you have to use the frontend for webpages

#@app.route("/")
#@app.route("/index")
#def index():
#    app.logger.debug("Main page entry")
#    return flask.render_template('calc.html')


#@app.errorhandler(404)
#def page_not_found(error):
#    app.logger.debug("Page not found")
#    flask.session['linkback'] = flask.url_for("index")
#    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    race_distance = request.args.get('race_distance', 999, type=float)
    #time_zone = request.args.get('utc_offset')
    date = arrow.get(request.args.get('day') + ' ' + request.args.get('time'), 'YYYY-MM-DD HH:mm', tzinfo='utc')
    print(date)
    app.logger.debug("km={}".format(km))
    app.logger.debug("brevet={}".format(race_distance))
    app.logger.debug("request.args: {}".format(request.args))
    app.logger.debug("date: {}".format(date))
    open_time = acp_times.open_time(km, race_distance, date)
    close_time = acp_times.close_time(km, race_distance, date)
    result = {"open": open_time, "close": close_time}
    print(f"Open: {open_time}, Close: {close_time}")
    return flask.jsonify(result=result)


#############

# Displaying the data
@app.route("/display")
def display_brevets():
    return flask.render_template('display_ajax.html')
#    global collection
#    if collection.count_documents({}) < 1:   # If the collection is empty, return our error
#        return flask.render_template('db_empty.html')
#    
    #Create a table of all the entries
#    table = []
#    for entrie in collection.find():
#        _id, miles, km, location, open_t, close_t = entrie.values()
#        print(km)
#        row = [miles, km, location, open_t, close_t]
#        for el in row:
#            print(el)
#        table.append(row)
#
#    return flask.render_template('display.html', table_body=table)

@app.route("/displayempty")

def display_empty():
    return flask.render_template('db_empty.html')

@app.route("/insert")
def add():
    global collection
    app.logger.debug("Got a JSON request")
    args = (request.args)
    #print(args)
    
    #Try working on this json
    new_dict = {}
    try:
        #Get the general stuff
        new_dict['distance'] = args["distance"]
        new_dict['begin_date'] = args['begin_date']
        new_dict['begin_time'] = args['begin_time'] 

        #Get the controls.
        #This is actually insane code but Jquery wasn't coperating and this is the easiest way 
        # I can think of to fix it
        control_list = []
        control_counter = 0
        control_string = f"control{control_counter}[miles]"
        while(control_string in args): 
            brevet = {"miles": args[control_string], 
                      "km": args[f"control{control_counter}[km]"],
                      "location": args[f"control{control_counter}[location]"],
                      "open_t": args[f"control{control_counter}[open_t]"],
                      "close_t": args[f"control{control_counter}[close_t]"],
                      }
            control_counter += 1
            control_string = f"control{control_counter}[miles]"
            control_list.append(brevet)
        #print(f"Got: {len(control_list)} items")
        #If we got nothing then don't add
        if(control_list == []):
            return flask.jsonify({ 'error': 'empty!' })
        new_dict['controls'] = control_list
        collection.insert_one(new_dict)
    except:
        return flask.jsonify({ 'error': 'failed' })
    return flask.jsonify( {'status': 'ok'} )

@app.route("/fetch/")
@app.route("/fetch/<filetype>")
@app.route("/listAll/")
@app.route("/listAll/<filetype>")
def fetch(filetype="json"):
    #Check if Top exists
    try:
        top = int(request.args.get('top'))
    except:
        top = None
    global collection
    #Grab the items and put them into a list
    items = []
    for brevet in collection.find():
            _id, distance, begin_date, begin_time, controls = brevet.values()
            for control in controls:
                miles, km, location, open_t, close_t = control.values()
                items.append({ 'distance': distance, 'begin_date': begin_date,
                              'begin_time': begin_time, 'miles': miles, 'km': km, 
                            'location': location, 'open_t': open_t, 
                            'close_t': close_t})
    #Sort them and chopthem if requested
    if top is not None:
        items = sorted(items, key=lambda x : calc_str_time(x['begin_date'], x['open_t']))
        items = items[:top]
    
    #If JSON, return a JSON
    if filetype == "json":
        return_json = {}
        rows = 0
        for brevet in items:
            return_json["row" + str(rows)] = { 'distance': brevet['distance'], 
                                              'begin_date': brevet['begin_date'],
                                              'begin_time': brevet['begin_time'], 
                                              'miles': brevet['miles'], 'km': brevet['km'], 
                                              'location': brevet['location'], 
                                              'open_t': brevet['open_t'], 
                                              'close_t': brevet['close_t']}
            rows += 1
        return flask.jsonify(return_json)
    elif filetype == "csv":
        csv_file = "distance,begin_date,begin_time,km,mi,location,open,close\n"
        for brevet in items:
                distance = brevet['distance']
                begin_date = brevet['begin_date']
                begin_time = brevet['begin_time']
                miles = brevet['miles'] 
                km = brevet['km'] 
                location = brevet['location'] 
                open_t = brevet['open_t'] 
                close_t = brevet['close_t']
                csv_file += f"""{distance},{begin_date},{begin_time},{km},{miles},{location},{open_t},{close_t}\n"""
        return flask.Response(csv_file, mimetype='text/csv')
    else:
        return "Error, type requested is invalid!"

@app.route("/listOpenOnly/")
@app.route("/listOpenOnly/<filetype>")
def fetch_openonly(filetype="json"):
    #Check if Top exists
    try:
        top = int(request.args.get('top'))
    except:
        top = None
    global collection
    #Grab the items and put them into a list
    items = []
    for brevet in collection.find():
            _id, distance, begin_date, begin_time, controls = brevet.values()
            for control in controls:
                miles, km, location, open_t, close_t = control.values()
                items.append({ 'distance': distance, 'begin_date': begin_date,
                              'begin_time': begin_time, 'miles': miles, 'km': km, 
                            'location': location, 'open_t': open_t})
    #Sort them and chopthem if requested
    if top is not None:
        items = sorted(items, key=lambda x : calc_str_time(x['begin_date'], x['open_t']))
        items = items[:top]
    
    #If JSON, return a JSON
    if filetype == "json":
        return_json = {}
        rows = 0
        for brevet in items:
            return_json["row" + str(rows)] = { 'distance': brevet['distance'], 
                                              'begin_date': brevet['begin_date'],
                                              'begin_time': brevet['begin_time'], 
                                              'miles': brevet['miles'], 'km': brevet['km'], 
                                              'location': brevet['location'], 
                                              'open_t': brevet['open_t']}
            rows += 1
        return flask.jsonify(return_json)
    elif filetype == "csv":
        csv_file = "distance,begin_date,begin_time,km,mi,location,open\n"
        for brevet in items:
                distance = brevet['distance']
                begin_date = brevet['begin_date']
                begin_time = brevet['begin_time']
                miles = brevet['miles'] 
                km = brevet['km'] 
                location = brevet['location'] 
                open_t = brevet['open_t'] 
                csv_file += f"""{distance},{begin_date},{begin_time},{km},{miles},{location},{open_t}\n"""
        return flask.Response(csv_file, mimetype='text/csv'),200
    else:
        return "Error, type requested is invalid!"

@app.route("/listCloseOnly/")
@app.route("/listCloseOnly/<filetype>")
def fetch_closeonly(filetype="json"):
    #Check if Top exists
    try:
        top = int(request.args.get('top'))
    except:
        top = None
    global collection
    #Grab the items and put them into a list
    items = []
    for brevet in collection.find():
            _id, distance, begin_date, begin_time, controls = brevet.values()
            for control in controls:
                miles, km, location, open_t, close_t = control.values()
                items.append({ 'distance': distance, 'begin_date': begin_date,
                              'begin_time': begin_time, 'miles': miles, 'km': km, 
                            'location': location, 'close_t': close_t})
    #Sort them and chopthem if requested
    if top is not None:
        items = sorted(items, key=lambda x : calc_str_time(x['begin_date'], x['close_t']))
        items = items[:top]
    
    #If JSON, return a JSON
    if filetype == "json":
        return_json = {}
        rows = 0
        for brevet in items:
            return_json["row" + str(rows)] = { 'distance': brevet['distance'], 
                                              'begin_date': brevet['begin_date'],
                                              'begin_time': brevet['begin_time'], 
                                              'miles': brevet['miles'], 'km': brevet['km'], 
                                              'location': brevet['location'], 
                                              'close_t': brevet['close_t']}
            rows += 1
        return flask.jsonify(return_json)
    elif filetype == "csv":
        csv_file = "distance,begin_date,begin_time,km,mi,location,close\n"
        for brevet in items:
                distance = brevet['distance']
                begin_date = brevet['begin_date']
                begin_time = brevet['begin_time']
                miles = brevet['miles'] 
                km = brevet['km'] 
                location = brevet['location'] 
                close_t = brevet['close_t']
                csv_file += f"""{distance},{begin_date},{begin_time},{km},{miles},{location},{close_t}\n"""
        return flask.Response(csv_file, mimetype='text/csv')
    else:
        return "Error, type requested is invalid!"



#Just a tester, basically just adds Sample_Data before working on the JS frontend
@app.route("/add_garbage")
def add_garbage():
    global collecton
    collection.insert_one({'distance': '200',
                          'begin_day': '2017-01-01',
                          'begin_time': '00:00',
                          'controls': [{'miles': '6.2', 'km' : '10', 'location' : 'name',
                           'open_t' : 'Sun 1/1 0:17',
                           'close_t ': 'Sun 1/1 1:30'
                           }]})
    return flask.redirect('/display')



app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    app.debug = True
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
