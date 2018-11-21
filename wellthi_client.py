from flask import Flask, request, jsonify, render_template, helpers, send_from_directory, make_response, session, \
    Response
from flask_bootstrap import Bootstrap
import requests
import json
from jinja2 import Template
from Models.Credentials import *
from Models.ChatMessages import *
import os
from Models.RedisConf import RedisConf
from Models.WellthiServer import *
import config
import sys


def create_app():
    app_instance = Flask(__name__)
    return app_instance


app = create_app()
Bootstrap(app)
app.jinja_env.add_extension('jinja2.ext.do')
cred = Credentials("", "")
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


@app.route('/')
def helloWorld():
    # print redis_instance.events
    print chat_server_version
    print redis_conf.events
    return "Hello world!!!"


@app.route('/load')
def detectFiles():
    return Biometric.ingest_biometric_files()


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
                        conversation_id = chat_server.chat_context['conversation_id']
                        todays_current_chat = \
                            MessageHelpers.get_today_chats(chat_server, '953d25b4-9170-47e5-b465-fc513f60ce1d')[
                                conversation_id]
                        # send evaluation
                        # assessment = Assessment()
                        assess = Assessment(userid,at,)


                        return make_response(render_template('wellthi_break.html', chat_message=response), 200, headers)
                    else:
                        return make_response(render_template('bootstrap_chat_index.html', chat_message=response), 200,
                                             headers)
                else:
                    return make_response(render_template('bootstrap_chat_index.html', chat_message=response), 200,
                                         headers)


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")
