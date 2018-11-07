from flask import Flask, request, jsonify, render_template, helpers, send_from_directory, make_response, session, \
    Response
from flask_bootstrap import Bootstrap
import requests
import json
from jinja2 import Template
from Models.Credentials import *
from Models.ChatMessages import *
from Models.RedisConf import RedisConf

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
chat_server_version = '2018-09-20'
chat_server = MessageHelpers(cred.username, cred.password, chat_server_version)
digital_ocean_endpoint = ""

redis_conf = RedisConf(host='localhost', port=6379, db=0)
redis_instance = redis_conf.connectRedis('stressed_event',
                        'happy_event')

print("Starting web server")

print ("events ", redis_conf)


@app.route('/server-endpoint/<url>')
def show_user_profile(url):
    digital_ocean_endpoint = str(url)
    return 'You have chosen to configure remote endpoint as %s' % url


@app.route('/')
def helloWorld():
    # print redis_instance.events
    print chat_server_version
    print redis_conf.events
    return "Hello world!!!"


@app.route('/events')
def getEvents():
    return json.dumps(redis_conf.events)

@app.route('/hello', methods=['GET', 'POST'])
def helloPost():
    if request.method == 'POST':
        json_data = request.get_json()
        email = json_data['email']
        password = json_data['password']
        payload = {"email": email,
                   "password": password}
        return jsonify(json.dumps(payload))
    else:
        return jsonify("{'hello' : 'world'}")


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
    headers = {'Content-Type': 'text/html'}
    return make_response(render_template('bootstrap_chat_index.html'), 200, headers)

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
            return make_response(render_template('bootstrap_chat_index.html'), 200, headers)
        else:
            if (cred.username == "" or cred.password == ""):
                print("please enter a username and password")
                return make_response(render_template('bootstrap_index.html'), 200, headers)
            else:  # post message
                message = request.form['chat_bot_text']
                response = chat_server.post_message('953d25b4-9170-47e5-b465-fc513f60ce1d', message)
                system_context = chat_server.chat_context['system']
                # if 'branch_exited_reason' in system_context:
                #     return make_response(render_template('wellthi_break.html', chat_message=response), 200, headers)
                # else:
                return make_response(render_template('bootstrap_chat_index.html', chat_message=response), 200, headers)


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
