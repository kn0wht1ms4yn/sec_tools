from flask import Flask, session, request, redirect, send_from_directory
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from functools import wraps
from os import path, environ
import sys, bcrypt, secrets, json

'''
config file must be in the form
{ "username":"", "password":"<hash>" }
hash must be bcrypt
import bcrypt
bcrypt.hashpw(b'meow', bcrypt.gensalt(rounds=12))
'''

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
        print(f'{f.__name__=}')
        if 'authenticated' in session and session['authenticated']:
            return f(*args, **kwargs)
        if f.__name__ == 'sock_msg':
            # FIXME: pretty sure I have to actually disconnect here
            return False
        return redirect('/login')
    return wrapper

''' --- Flask --- '''
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
socketio = SocketIO(app)
RELAY_ON = False
STATIC_DIR = path.join(app.root_path, '../frontend')

''' --- HTTP --- '''
@app.route('/')
@auth_required
def index():
    return send_from_directory(path.join(STATIC_DIR), 'index.html')

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
@auth_required
def sock_msg(msg):
    print(f'connect recvd: {msg}')

if __name__ == '__main__':
    server_config = {
            'host': '127.0.0.1',
            'port': 8888,
            'debug': True
            }
    socketio.run(app, **server_config)
