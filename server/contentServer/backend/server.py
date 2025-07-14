from flask import Flask, redirect, session, request, send_from_directory, jsonify
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from os import path, makedirs, listdir, remove, environ
import sys
from functools import wraps
import secrets
import bcrypt
import json
import time

''' --- load credentials from config file --- '''
config_filename = environ.get('APP_CONFIG_FILE', False)
if not config_filename:
    print('missing environment variable APP_CONFIG_FILE')
    exit() 
if not path.exists(config_filename):
    print(f'config file does not exist: {config_filename}')
    exit()
with open(config_filename, 'r') as file:
    try:
        conf_obj = json.loads(file.read())
    except:
        print('unable to parse conf file')
        exit()
conf_username = conf_obj['username']
conf_password = conf_obj['password']

def auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'authenticated' in session and session['authenticated']:
            return f(*args, **kwargs)
        if f.__name__ == 'sock_msg':
            # FIXME: pretty sure I have to actually disconnect here
            return False
        return redirect('/login')
    return wrapper

''' --- flask --- '''
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
socketio = SocketIO(app)

STATIC_DIR = path.join(app.root_path, '../frontend')
FILES_DIR = '/tmp/contentServer_files'

# make files dir
makedirs(FILES_DIR, exist_ok=True)

''' --- Flask --- '''
@app.route('/login', methods=['GET', 'POST'])
def login():

    # POST
    if request.method == 'POST':
        if 'username' not in request.form or 'password' not in request.form:
            return redirect('/login')
        username = request.form['username']
        password = request.form['password']

        correct_username = username == conf_username
        correct_password = bcrypt.checkpw(password.encode(), conf_password.encode())

        if correct_username and correct_password:
            session['authenticated'] = True
            return redirect('/')
        else:
            session['authenticated'] = False
            return redirect('/login')

    # GET
    return send_from_directory(path.join(STATIC_DIR), 'login.html')


''' --- protected paths ---'''
@app.route('/')
@auth_required
def index():
    return send_from_directory(path.join(STATIC_DIR), 'index.html')

@app.route('/getFiles', methods=['GET'])
@auth_required
def getFiles():
    files = listdir(FILES_DIR)
    return jsonify({ 'files': files })

@app.route('/getFile/<string:filename>', methods=['GET'])
@auth_required
def getFile(filename):
    with open(path.join(FILES_DIR, filename)) as file:
        file_content = file.read()
    return jsonify({ 'content': file_content })

@app.route('/createFile', methods=['POST'])
@auth_required
def createFile():
    data = request.get_json()
    filename = data['filename']
    if '/' in filename or '..' in filename:
        return 'NOPE'
    open(path.join(FILES_DIR, filename), 'a').close()
    return 'OK'

@app.route('/deleteFile', methods=['POST'])
@auth_required
def deleteFile():
    data = request.get_json()
    filename = data['filename']
    if '/' in filename or '..' in filename:
        return 'NOPE'
    remove(path.join(FILES_DIR, filename))
    return 'OK'

@app.route('/saveFile', methods=['POST'])
@auth_required
def saveFile():
    data = request.get_json()
    filename = data['filename']
    content = data['content']
    if '/' in filename or '..' in filename:
        return 'NOPE'
    with open(path.join(FILES_DIR, filename), 'w') as file:
        file.write(content + '\n')

    return 'OK'

''' --- public paths --- '''
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

''' --- socketIO --- '''
@socketio.on('connect')
@auth_required
def sock_msg(msg):
    print(f'connect recvd: {msg}')

if __name__ == '__main__':
    server_config = {
            'host': '127.0.0.1',
            'port': 8899,
            'debug': True
            }
    socketio.run(app, **server_config)
