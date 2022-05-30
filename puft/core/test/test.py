from pytest import fixture
from flask_socketio import SocketIOTestClient
from flask.testing import FlaskClient

from puft.core.app.puft import Puft
from puft.core.db.db import Db
from puft.tools.get_root_path import get_root_path
from puft.core.sock.sock import socket


class Test:
    @fixture
    def app(self):
        app: Puft = Puft.instance()
        yield app

    @fixture
    def db(self, app: Puft):
        db: Db = Db.instance()

        with app.app_context():
            db.drop_all()
            db.create_all()

        yield db

        with app.app_context():
            db.drop_all()

    @fixture
    def client(self, app: Puft) -> FlaskClient:
        return app.test_client()

    @fixture
    def sock_client(self, app: Puft) -> SocketIOTestClient:
        # https://github.com/miguelgrinberg/Flask-SocketIO/blob/main/test_socketio.py
        return socket.test_client(app.get_native_app())

    @fixture
    def root_path(self) -> str:
        return get_root_path()
