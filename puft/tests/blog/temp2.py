def test_temp():
    from flask import Flask
    from flask_socketio import SocketIO
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    socketio = SocketIO(app)
    socketio.on_event('connect', lambda: print('Connect'), '/temp')
    socketio.on_event('temp', lambda: print('Test'), '/temp')
    client = socketio.test_client(app)
    client.connect('/temp')
    socketio.emit('temp', 'hello', namespace='/temp')
    received = client.get_received('/temp')
    assert False, received
