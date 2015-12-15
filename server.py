#!/usr/bin/env python3

import os
from bottle import Bottle, static_file
from rest import api

app = Bottle()

@app.route('/')
def send_index():
    return send_static('index.html')

@app.route('/<filename:path>')
def send_static(filename):
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    return static_file(filename, root=root)

app.merge(api.api)
app.run(host='localhost', port=8080, debug=True)
