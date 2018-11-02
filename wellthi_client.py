from flask import Flask, request, jsonify,render_template,helpers,send_from_directory,make_response
from flask_bootstrap import Bootstrap
import requests
import json
from jinja2 import Template

app = Flask(__name__)   # Initiate app
Bootstrap(app)
app.jinja_env.add_extension('jinja2.ext.do')

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

@app.route('/index')
def indexPage():
    headers = {'Content-Type': 'text/html'}
    return make_response(render_template('bootstrap_index.html'),200,headers)


if __name__ == '__main__':
    app.run()
