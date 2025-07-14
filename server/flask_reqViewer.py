'''
    
    Simple flask app that prints request headers and any GET/POST data.

'''
from flask import Flask, request
import logging
app = Flask(__name__)

# supress standard flask logs
logging.getLogger('werkzeug').setLevel(logging.ERROR)

@app.route('/', methods=['GET','POST'])
@app.route('/<path:subpath>', methods=['GET','POST'])
def index(subpath):
    print('-'*60)

    print(f'{request.method} {request.path} {request.environ.get("SERVER_PROTOCOL")}')
    for header in request.headers:
        print(f'{header[0]}: {header[1]}')
    
    print()

    content_type = request.content_type
    if content_type == 'application/json':
        print(f'JSON: {request.get_json()}')

    elif content_type == 'application/x-www-form-urlencoded':
        form_data = map(lambda x: f'{x}={request.form[x]}', request.form)
        form_data = '&'.join(form_data)
        print(f'POST params: {form_data}')
    
    if len(request.args):
        GET_data = map(lambda x: f'{x}={request.args[x]}', request.args)
        GET_data = '&'.join(GET_data)
        print(f'GET params: {GET_data}')
    
    print('-'*60)
    return 'meow'

app.run('0.0.0.0', port=89, debug=True)