#!/usr/bin/env python3

import os
from bottle import Bottle, static_file, response
from rest import api

app = Bottle()


@app.hook('after_request')
def enable_cors(r=None):
    if r is None:
        r = response
    r.add_header('Access-Control-Allow-Origin', '*')


@app.route('/')
def send_index():
    return send_static('index.html')


@app.route('/<filename:path>')
def send_static(filename):
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    r = static_file(filename, root=root)
    r.set_header('Cache-control', 'private, max-age=0, no-cache')
    r.set_header('Pragma', 'no-cache')
    return r

app.merge(api.api)
app.run(host='localhost', port=8081, debug=True, reloader=True)
