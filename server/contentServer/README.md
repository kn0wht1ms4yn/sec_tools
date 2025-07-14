##### description
- simple web app that allows creating of files (html, js, css)

##### running the server
- gunicorn -b 127.0.0.1:8899 -k gevent -w 1 server:app

##### config file
- requires a config file to with credentials
- the path to this config file must be stored in APP_CONFIG_FILE environment variable
- must be in the following format where the password is bcrypt
```
{ "username": "", "password": "" }
```