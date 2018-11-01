from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

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


if __name__ == '__main__':
    app.run()
