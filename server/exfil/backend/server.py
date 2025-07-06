from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from os import path
import json
import time
import sys

app = Flask(__name__)
app.config['SECRET_LEY'] = 'FIXME: CHANGE_THIS_FOR_PROD'
socketio = SocketIO(app)

RELAY_ON = False

STATIC_DIR = path.join(app.root_path, '../frontend')

''' --- Flask --- '''
@app.route('/')
def index():
    return send_from_directory(path.join(STATIC_DIR), 'index.html')

@app.route('/exfil', methods=['GET','POST'])
@app.route('/exfil/<path:subpath>', methods=['GET','POST'])
def exfil(subpath=''):
    # headers
    headers = ''
    for header in request.headers:
        headers += f'<span class="text-warning">{header[0]}</span>: {header[1]}<br />'
    
    # get data
    get_data = ''
    if len(request.args):
        get_data += '?'
        data = map(lambda x: f'{x}={request.args[x]}', request.args)
        data = '&'.join(data)
        get_data += data

    # body data
    body_data = request.data.decode()

    # construct response
    path = f'<span class="text-info">{request.method} {request.path}{get_data} {request.environ.get("SERVER_PROTOCOL")}</span>'
    resp = f'{path}<br />'
    resp += f'{headers}<br />'
    resp += f'{body_data}'

    socketio.send({ 'req': resp })
    return 'OK'

''' --- socketIO --- '''
@socketio.on('connect')
def sock_msg(msg):
    print(f'connect recvd: {msg}')

server_config = {
        'host': '0.0.0.0',
        'port': 8888,
        'debug': True
        }


if (len(sys.argv) == 3):
    certFile = sys.argv[1]
    keyFile = sys.argv[2]
    server_config['ssl_context'] = (certFile, keyFile)

socketio.run(app, **server_config)
