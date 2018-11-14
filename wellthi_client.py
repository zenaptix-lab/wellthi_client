from flask import Flask, request, jsonify, render_template, helpers, send_from_directory, make_response, session, \
    Response
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
from hrv.classical import frequency_domain, time_domain
from Models.RedisConf import RedisConf
import config

import sys


def create_app():
    app_instance = Flask(__name__)
    from Models.RedisConf import RedisConf
    # redis_conf = RedisConf(host='localhost', port=6379, db=0).connectRedis('stressed_event',
    #                                                                        'happy_event')
    return app_instance


app = create_app()
Bootstrap(app)
app.jinja_env.add_extension('jinja2.ext.do')
cred = Credentials("", "")
known_files = config.FILE_DROP_CONFIG['known_files']
path_load = config.FILE_DROP_CONFIG['path_load']
chat_server_version = config.CHAT_BOT_CONFIG['chat_server_version']
chat_server = MessageHelpers(cred.username, cred.password, chat_server_version)
digital_ocean_endpoint = ""

redis_conf = RedisConf(config.REDIS_CONFIG['host'], config.REDIS_CONFIG['port'], config.REDIS_CONFIG['db'])
redis_instance = redis_conf.connectRedis(config.REDIS_CONFIG['events'])

print("Starting web server")
print ("Redis subscribed to events : ", redis_conf.events)


@app.route('/server-endpoint/<url>')
def show_user_profile(url):
    digital_ocean_endpoint = str(url)
    return 'You have chosen to configure remote endpoint as %s' % url


def getRRIntervals(data):
    # data is read from the csv, and the 2nd column indicates when heart beats occurred with a 'B'

    # Select heartbeats column
    beats = data.loc[:, 1] == 'B'

    # get the index numbers of when "beats" column is    True
    beat_indices_orig = list(beats[beats].index)

    # shift index numbers by 1
    beat_indices_shifted = [x + 1 for x in beat_indices_orig]

    # take the difference between original and shifted beats. This removes consecutive beats in original data
    beat_indices = list(set(beat_indices_orig) - set(beat_indices_shifted))
    beat_indices.sort()

    # Now process RR-intervals (difference in time between beats):
    rr_indices = [t - s for s, t in zip(beat_indices, beat_indices[1:])]
    # This takes the difference between consecutive elements in a list (gets number of samples between beats)

    # There are 60 samples per second, so translate above into milliseconds between beats (RR intervals):
    rr = [i * 1000 / 60.0 for i in rr_indices]
    return rr


# Process the time domain parameters of HRV from the RR-intervals
def getHRV_TimeDomain(rr_intervals):
    return time_domain(rr_intervals)


# Process the frequency domain parameters of HRV from the RR-intervals
def getHRV_FreqDomain(rr_intervals):
    return frequency_domain(rri=rr_intervals, fs=4.0, method='welch', interp_method='cubic', detrend='linear')


def evaluateStress(rr_sample):
    s1 = 0  # light indicator of stress
    s2 = 0  # hard indicator of stress

    # Time domain indicators:
    timeDomain = getHRV_TimeDomain(rr_sample)

    rr_mean = np.mean(rr_sample)
    if rr_mean < 640:
        s2 = s2 + 1
    else:
        if rr_mean < 780: s1 = s1 + 1

    sdnn = timeDomain["sdnn"]
    if sdnn < 20:
        s2 = s2 + 1
    else:
        if sdnn < 40: s1 = s1 + 1

    rmssd = timeDomain["rmssd"]
    if rmssd < 16: s2 = s2 + 1

    # Time domain indicators:
    freqDomain = getHRV_FreqDomain(rr_sample)

    hf = freqDomain["hf"]
    if hf < 465:
        s2 = s2 + 1
    else:
        if hf < 700: s1 = s1 + 1

    vlf = freqDomain["vlf"]
    if vlf < 200:
        s2 = s2 + 1
    else:
        if vlf < 300: s1 = s1 + 1

    lf_hf = freqDomain["lf_hf"]
    if lf_hf > 4:
        s2 = s2 + 1
    else:
        if lf_hf > 2.5: s1 = s1 + 1

    #  Summarise result into a binary indicator. If s2 >= 1, or if s1 >= 2, then stressed:
    stressed = 1 if (s2 >= 1) or (s1 >= 2) else 0

    result = {'status': stressed, 'val1': rr_mean, 'val2': sdnn, 'val3': rmssd, 'val4': hf, 'val5': vlf, 'val6': lf_hf}

    return result


@app.route('/')
def helloWorld():
    # print redis_instance.events
    print chat_server_version
    print redis_conf.events
    return "Hello world!!!"


@app.route('/load')
def detectFiles():
    files = os.listdir(config.FILE_DROP_CONFIG['path_load'])
    for f in files:
        if f not in known_files:
            print("let's go! Read file: " + f)
            data = pd.read_csv(path_load + f, header=None)
            known_files.append(f)

            user_id = config.FILE_DROP_CONFIG['user_id']
            file_timestamp = config.FILE_DROP_CONFIG['file_timestamp']

            rr = getRRIntervals(data)
            # toPrint = np.array2string(np.array(rr))

            # Group rr into 2 minute intervals
            rr_sum = np.cumsum(rr)
            print(rr_sum)

            sample_size = 150000  # milliseconds

            # the last element of the cumulative sum of rr is equal to the total duration of the recording.
            # We want to group the rr values by 2.5 minutes, so that the parameters can be generated for each group
            print(range(0, int(rr_sum[len(rr_sum) - 1].item()), sample_size))

            toPrint = []

            for i in range(0, int(rr_sum[len(rr_sum) - 1].item()), sample_size):
                rr_sum_subset = [(i <= s) and (s < (i + 1) * sample_size) for s in rr_sum]
                rr_temp = np.array(rr)
                rr_sample = list(rr_temp[rr_sum_subset])
                if len(rr_sample) > 80:  # Let's require at least 80 rr's to process, in case last group only has a few
                    result = evaluateStress(rr_sample)

                    result['id'] = user_id
                    result['from'] = file_timestamp + i / 1000
                    result['to'] = file_timestamp + (i + sample_size) / 1000

                    print(result)
                    toPrint.append(result)
                    # print(getHRV_FreqDomain(rr_sample))  # send result
                    # print(getHRV_TimeDomain(rr_sample))

            # Frequency domain
            # toPrint = json.dumps(getHRV_FreqDomain(rr))

            for variables in toPrint:
                # print str(variables)
                r = requests.post(config.WELLTHI_SERVER_CONFIG['biometric_data_endpoint'] + user_id,
                                  headers={'content-type': 'application/json'},
                                  data=json.dumps(variables))
                print "responce to request: ", r
            return json.dumps(toPrint)

    return "Okay, no new files"


@app.route('/events')
def getEvents():
    return json.dumps(redis_conf.events)


@app.route('/hello', methods=['GET', 'POST'])
def helloPost():
    if request.method == 'POST':
        json_data = request.get_json()
        print("Sent JSON DATA :", json.dumps(json_data))
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


@app.route('/wellthi_break')
def wellthi_break():
    headers = {'Content-Type': 'text/html'}
    return make_response(render_template('wellthi_break.html'), 200, headers)


@app.route('/chat_bot_page')
def chat_bot():
    print("redis events lenghts : ", redis_conf.events)
    if len(redis_conf.events) > 0:
        headers = {'Content-Type': 'text/html'}
        response = chat_server.post_message('953d25b4-9170-47e5-b465-fc513f60ce1d', redis_conf.events[0])
        print ("chat bot response : ", response)
        redis_conf.events = []
        return make_response(render_template('bootstrap_chat_area.html', chat_message=response), 200, headers)
    else:
        return ('', 200)


@app.route('/return_to_chatbot', methods=['GET'])
def return_to_chatbot():
    headers = {'Content-Type': 'text/html'}
    if (cred.username == "" or cred.password == ""):
        return make_response(render_template('bootstrap_index.html'), 200, headers)
    else:
        return make_response(render_template('bootstrap_chat_index.html', chat_message="Welcome back"), 200,
                             headers)


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
            chat_server.update_watson_config(cred.username, password, chat_server_version)
            valid_response = cred.check_password(chat_server)

            if str(valid_response) == "valid":
                return make_response(render_template('bootstrap_chat_index.html'), 200, headers)
            else:
                return make_response(render_template('bootstrap_index.html'), 200, headers)
        else:
            if (cred.username == "" or cred.password == ""):
                print("please enter a username and password")
                return make_response(render_template('bootstrap_index.html'), 200, headers)
            else:  # post message
                message = request.form['chat_bot_text']
                response = chat_server.post_message('953d25b4-9170-47e5-b465-fc513f60ce1d', message)
                system_context = chat_server.chat_context['system']
                if 'branch_exited_reason' in system_context:
                    if "wellthi break" in str(response).lower():
                        print("EXIT chat bot session")
                        return make_response(render_template('wellthi_break.html', chat_message=response), 200, headers)
                    else:
                        return make_response(render_template('bootstrap_chat_index.html', chat_message=response), 200,
                                             headers)
                else:
                    return make_response(render_template('bootstrap_chat_index.html', chat_message=response), 200,
                                         headers)


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
