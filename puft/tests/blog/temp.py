import json
import unittest

from flask import Flask, session, request, json as flask_json
from flask_socketio import SocketIO, send, emit, join_room, leave_room, \
    Namespace, disconnect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

def on_temp(data):
    print('TEMP')

socketio.on_event('temp', on_temp, namespace='/temp')

def test_emit_class_based():
    client = socketio.test_client(app)
    print(socketio.server.__dict__['handlers'])
    client.connect('/temp')
    client.emit('temp', {'a': 'b'}, namespace='/temp')
    received = client.get_received('/temp')
    assert False, received
