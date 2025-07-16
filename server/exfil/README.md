
##### description
- a simple web app that recvs a request and shows it in a `<textarea>`
- to log a request send it to `/exfil`

##### running the server
- gunicorn -b 127.0.0.1:8899 -k gevent -w 1 server:app

##### config file
- requires a config file to with credentials
- the path to this config file must be stored in APP_CONFIG_FILE environment variable
- must be in the following format where the password is bcrypt
```
{ "username": "", "password": "" }
```

