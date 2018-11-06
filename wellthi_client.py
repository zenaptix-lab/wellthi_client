from flask import Flask, request, jsonify, render_template, helpers, send_from_directory, make_response, session
from flask_bootstrap import Bootstrap
import requests
import json
from jinja2 import Template
from Models.Credentials import *
from Models.ChatMessages import *
import os
import pandas as pd
from hrv.filters import moving_average
import numpy as np
from hrv.classical import frequency_domain

app = Flask(__name__)  # Initiate app
Bootstrap(app)
app.jinja_env.add_extension('jinja2.ext.do')
cred = Credentials("", "")
known_files = [".DS_Store"]
path_load = "/Users/mouritsdebeer/Desktop/watchme/" # "/path/to/listen/folder"

print("Starting web server")


def getRRIntervals(data):
    data[1].replace('B', 1, inplace=True)
    data[1].replace(' ', 0, inplace=True)
    # convert the B's, which indicate heart beats, to 1

    beat_indices = []
    for i in range(0, len(data[1])):
        if data[1][i] == 1:
            beat_indices.append(data[0][i])
            data[1][i+1] = 0
    # remove the second B

    rr = []
    for i in range(1, len(beat_indices)):
        rr.append(1000.0 * (beat_indices[i] - beat_indices[i-1]) / 60.0)
    # the rr intervals
    return rr


# Process the time domain parameters of HRV from the RR-intervals
def getHRV_TimeDomain(rr_intervals):
    return rr_intervals


# Process the frequency domain parameters of HRV from the RR-intervals
def getHRV_FreqDomain(rr_intervals):
    return frequency_domain(rri=rr_intervals, fs=4.0, method='welch', interp_method='cubic', detrend='linear')


@app.route('/')
def helloWorld():
    return "Hello world!!!"


@app.route('/load')
def detectFiles():
    files = os.listdir(path_load)
    for f in files:
        if f not in known_files:
            print("let's go! Read file: " + f)
            data = pd.read_csv(path_load + f, header=None)
            known_files.append(f)

            rr = getRRIntervals(data)
            # toPrint = np.array2string(np.array(rr))

            #Frequency domain
            toPrint = json.dumps(getHRV_FreqDomain(rr))

            #post result to
            r = requests.post('http://0.0.0.0:5000/hello', headers={'content-type': 'application/json'}, data=toPrint)
            print("responce to request: ", r)
            #return r.json
    return "Okay, no new files"


@app.route('/hello', methods=['GET', 'POST'])
def helloPost():
    if request.method == 'POST':
        json_data = request.get_json()
        print("$$$$$$$$$$$$$$ :"+str(jsonify(json.dumps(json_data))))
        return jsonify(json_data)
    else:
        return jsonify(json.dumps(request.get_json()))


@app.route('/test')
def jsonSend():
    json_data = {
        "email": "rikus",
        "password": "userpass123"
    }
    headers = {'content-type': 'application/json'}
    r = requests.post('http://0.0.0.0:5000/hello', headers=headers, data=json.dumps(json_data))
    return r.json()


@app.route('/static/<resource_name>')
def getResource(resource_name):
    return send_from_directory('static', resource_name)


@app.route('/index', methods=['POST', 'GET'])
def indexPage():
    error = None
    headers = {'Content-Type': 'text/html'}
    if request.method == 'GET':  # load /index page
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('bootstrap_index.html'), 200, headers)

    else:
        if (request.form.get('username') and request.form.get('password')):
            username = request.form['username']
            password = request.form['password']
            cred.update(username, password)
            return make_response(render_template('bootstrap_index.html'), 200, headers)
        else:
            if (cred.username == "" or cred.password == ""):
                print("please enter a username and password")
                return make_response(render_template('bootstrap_index.html'), 200, headers)
            else:  # post message
                message = request.form['chat_bot_text']
                response = MessageHelpers("d01d68b2-3864-4401-a26d-92b10ef74e48", "FUWYZmMJmjGF",
                                          '2018-09-20').post_message('953d25b4-9170-47e5-b465-fc513f60ce1d',message )
                return make_response(render_template('bootstrap_index.html', chat_message=response), 200, headers)


if __name__ == '__main__':
    app.run()
