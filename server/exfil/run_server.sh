#!/bin/bash
gunicorn -b 127.0.0.1:8888 -k gevent -w 1 backend.server:app