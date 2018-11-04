from flask import Flask, request, jsonify,render_template,helpers,send_from_directory,make_response, session
from flask_bootstrap import Bootstrap
import requests
import json
from jinja2 import Template
from Models.Credentials import *

app = Flask(__name__)   # Initiate app
Bootstrap(app)
app.jinja_env.add_extension('jinja2.ext.do')
cred = Credentials("","")

print("Starting web server")

@app.route('/')
def helloWorld():
    return "Hello world!!!"

@app.route('/hello', methods=['GET','POST'])
def helloPost():
    if request.method == 'POST':
        json_data = request.get_json()
        email = json_data['email']
        password = json_data['password']
        payload = {"email": email,
                   "password":password}
        return jsonify(json.dumps(payload))
    else:
        return jsonify("{'hello' : 'world'}")


@app.route('/test')
def jsonSend ():
    json_data = {
        "email" : "rikus",
        "password" : "userpass123"
    }
    headers = {'content-type': 'application/json'}
    r = requests.post('http://0.0.0.0:5000/hello', headers=headers, data=json.dumps(json_data))

    return r.json()


@app.route('/static/<resource_name>')
def getResource(resource_name):
    return send_from_directory('static',resource_name)

@app.route('/index',methods=['POST','GET'])
def indexPage():
    error = None
    headers = {'Content-Type': 'text/html'}
    if request.method == 'GET' : # load /index page
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('bootstrap_index.html'),200,headers)

    else:
        if(request.form.get('username')== True & request.form.get('password') == True):
            username = request.form['username']
            password = request.form['password']
            cred = (username,password)
            return make_response(render_template('bootstrap_index.html'),200,headers)
        else:
            print("please enter a username and password")
            return make_response(render_template('bootstrap_index.html'),200,headers)


if __name__ == '__main__':
    app.run()
