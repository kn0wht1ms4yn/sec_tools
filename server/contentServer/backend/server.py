from flask import Flask, session, request, send_from_directory, jsonify
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from os import path, makedirs, listdir, remove
import secrets
import json
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
socketio = SocketIO(app)

STATIC_DIR = path.join(app.root_path, '../frontend')
FILES_DIR = '/tmp/contentServer_files'

# make files dir
makedirs(FILES_DIR, exist_ok=True)

''' --- Flask --- '''
@app.route('/')
def index():
    return send_from_directory(path.join(STATIC_DIR), 'index.html')

@app.route('/getFiles', methods=['GET'])
def getFiles():
    files = listdir(FILES_DIR)
    return jsonify({ 'files': files })

@app.route('/getFile/<string:filename>', methods=['GET'])
def getFile(filename):
    with open(path.join(FILES_DIR, filename)) as file:
        file_content = file.read()
    return jsonify({ 'content': file_content })

@app.route('/createFile', methods=['POST'])
def createFile():
    data = request.get_json()
    filename = data['filename']
    if '/' in filename or '..' in filename:
        return 'NOPE'
    open(path.join(FILES_DIR, filename), 'a').close()
    return 'OK'

@app.route('/deleteFile', methods=['POST'])
def deleteFile():
    data = request.get_json()
    filename = data['filename']
    if '/' in filename or '..' in filename:
        return 'NOPE'
    remove(path.join(FILES_DIR, filename))
    return 'OK'

@app.route('/saveFile', methods=['POST'])
def saveFile():
    data = request.get_json()
    filename = data['filename']
    content = data['content']
    if '/' in filename or '..' in filename:
        return 'NOPE'
    with open(path.join(FILES_DIR, filename), 'w') as file:
        file.write(content + '\n')

    return 'OK'

@app.route('/file/<string:filename>', methods=['GET'])
@app.route('/file', methods=['GET'])
@app.route('/file/', methods=['GET'])
def file(filename='index.html'):
    if '/' in filename or '..' in filename:
        return 'NOPE'
    
    src_ip = request.remote_addr
    url = request.url

    socketio.send({ 'req': f'[{src_ip}] {url}' })

    return send_from_directory(FILES_DIR, filename)

@app.route('/exfil',methods=['GET','POST'])
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
        'host': '127.0.0.1',
        'port': 8899,
        'debug': True
        }
socketio.run(app, **server_config)
