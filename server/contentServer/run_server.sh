#!/bin/bash
export APP_CONFIG_FILE=~/servers.conf
gunicorn -b 127.0.0.1:8899 -k gevent -w 1 backend.server:app
