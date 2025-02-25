'''

    Simple flask app that redirects a request somewhere.

'''
import argparse
from flask import Flask, redirect, cli
app = Flask(__name__)

# supress 'Serving' and 'Debug mode' lines
cli.show_server_banner = lambda *args, **kwargs: None

# setup arg parser
parser = argparse.ArgumentParser(
    prog='flask_redirector.py',
    description='flask app that redirects a request somewhere'
)
parser.add_argument('-i', '--ipAddress', metavar='', default='0.0.0.0', help='ip address to listen on')
parser.add_argument('-p', '--port', metavar='', default=8081, help='port to listen on')
parser.add_argument('-r', '--redirectTo', metavar='', default='http://google.com', help='address to redirect to')
parser.add_argument('-u', '--uri', metavar='', default='/', help='URI to receive request at')
args = parser.parse_args()

# get args
ipAddress = args.ipAddress
port = args.port
redirectTo = args.redirectTo
uri = args.uri

@app.route(uri)
def index():
    return redirect(redirectTo)

start_msg = f'Starting redirect server from http://{ipAddress}:{port}{uri} to {redirectTo}'
print('-'*len(start_msg))
print(start_msg)
print('-'*len(start_msg))
app.run(host=ipAddress, port=port)