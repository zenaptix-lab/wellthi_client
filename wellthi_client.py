from flask import Flask, request, jsonify

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
        return jsonify(email, password)
    else:
        return jsonify("{'hello' : 'world'}")



if __name__ == '__main__':
    app.run()
