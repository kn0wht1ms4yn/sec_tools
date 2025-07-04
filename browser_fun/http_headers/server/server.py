from flask import Flask, request, jsonify, make_response, send_from_directory
import os

app = Flask(__name__)
STATIC_DIR = os.path.join(app.root_path, '../frontend')
print(f'{STATIC_DIR=}')

headers = {}
content = ''

@app.route("/", methods=[ 'GET' ])
def index():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route("/doHeaders", methods=[ 'POST' ])
def doHeaders():

    global headers
    global content

    jsonData = request.json

    if 'content' not in jsonData or 'headers' not in jsonData:
        return jsonify({'error': "request must include 'content' and 'headers' fields."})

    headers = jsonData['headers']
    content = jsonData['content']

    return 'OK'

@app.route("/show", methods=[ 'GET' ])
def show():
    resp = make_response(content)
    for header in headers:
        resp.headers[header] = headers[header]

    return resp


app.run(host='0.0.0.0', port='8888', debug=True)