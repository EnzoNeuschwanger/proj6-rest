"""
Frontend Replacement for RUSA ACP brevet time calculator

"""

import flask
from flask import request
import config

import os      # For getting enviroment variables

import logging

import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import requests



###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()
app.secret_key = CONFIG.SECRET_KEY

api_server = os.environ['API_PORT_5000_TCP_ADDR']
api_port = '5001'
api_url = "http://" + api_server + ':' + api_port


###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] = flask.url_for("index")
    return flask.render_template('404.html'), 404

# server API access

@app.route("/insert")
def add():
    app.logger.debug("Got a JSON request")
    args = (request.args.to_dict())
    #passing it to the api_serve
    result = requests.get(api_url + "/insert", args).json()
    print(result)
    return flask.jsonify(result)

@app.route("/fetch")
def fetch():
    args = request.args
        #Get the arguments of this request
    try:
        fetch_type = args['type']
    except:
        fetch_type = "listAll"
    try:
        print(args['csv'])
        if args['csv'] == 'true':
            fetch_csv = True
        else:
            fetch_csv = False
    except:
        fetch_csv = False
    try:
        print(args['top'])
        fetch_top = int(args['top'])
    except:
        fetch_top = None

    #Build the request string
    request_string = api_url + '/' + fetch_type + '/'
        
    if fetch_csv == True: #If CSV is requested
        request_string += "csv"

    #Add top arguments
    if fetch_top is not None:
        request_string += "?top=" + str(fetch_top)
    
    print(f"The Request: {request_string}")
    #Make the request
    return_val = requests.get(request_string)
    return_type = return_val.headers['Content-Type']
    print(return_type)
    if return_type == "application/json":
        return flask.jsonify(return_val.json())
    elif return_type == "text/csv; charset=utf-8":
        return flask.Response(return_val.text, mimetype="text/csv")
    else:
        return flask.jsonify({"status": "failed"})
    

#############

# Displaying the data
@app.route("/display")
def display_brevets():
    return flask.render_template('display_ajax.html')

@app.route("/displayempty")
def display_empty():
    return flask.render_template('db_empty.html')

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




app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    app.debug = True
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
