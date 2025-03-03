'''
    Simple flask app that serves a single file with Access-Control-Allow-Origin: *
'''
import argparse, os
from flask import Flask, Response, cli
app = Flask(__name__)
from flask_cors import CORS
CORS(app)

# supress 'Serving' and 'Debug mode' lines
cli.show_server_banner = lambda *args, **kwargs: None

# setup arg parser
parser = argparse.ArgumentParser(
    prog='flask_redirector.py',
    description='flask app that redirects a request somewhere'
)
parser.add_argument('-f', '--file', metavar='', default='script.js', help='file to serve')
parser.add_argument('-p', '--path', metavar='', default='/', help='path to serve file at')
parser.add_argument('-P', '--port', metavar='', default='80', help='port to run server on')
parser.add_argument('-ip', '--ipAddress', metavar='', default='0.0.0.0', help='ip address for server to listen on')
args = parser.parse_args()

# get args
file = args.file
path = args.path
ip = args.ipAddress
port = args.port

# define mimetypes
mimetypes = {
    '.js':   'text/javascript',
    '.html': 'text/html',
    '.css':  'text/css',
    '.txt':  'text/plain'
}

# check path starts with /
if path[0] != '/':
    print('Path must start with /')
    exit()

# check file exists
file_exists = os.path.exists(file)
if not file_exists:
    print(f'File does not exist: {file}')
    exit()

# get mimetype
ext = os.path.splitext(file)[1]
valid_mimetype = ext in mimetypes
if not valid_mimetype:
    mimetype = mimetypes['.txt']
    print(f'Could not find mimetype for {ext}, using {mimetype}')
else:
    mimetype = mimetypes[ext]

# get file contents
with open(file) as f:
    file_contents = f.read()

# print setup
print(f'Starting server for {file} on http://{ip}:{port}{path}')

# serve file
@app.route(path)
def index():
    return Response(file_contents, mimetype=mimetype)

app.run(ip, port=port)