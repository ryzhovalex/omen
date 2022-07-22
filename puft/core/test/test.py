from pytest import fixture
from flask_socketio import SocketIOTestClient
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from puft.core.app.puft import Puft
from puft.core import validation, parsing
from puft.core.db.db import Db
from puft.core.sock.socket import Socket
from puft.tools.get_root_dir import get_root_dir


class Test:
    # @fixture
    # def request(self, app: Puft, client: FlaskClient) -> TestResponse:
    #     def inner(request: str, asserted_status_code: int):
    #         response: TestResponse
    #         method: str
    #         url: str

    #         validation.validate

    #         # Request example: 'get /users/1'
    #         method, url = request.split(' ')

    #         # Also can accept uppercase 'GET ...'
    #         method = method.lower()

    #         match method:
    #             case 'get':
    #                 response = app.test_client().get()
    #             case

    #     return inner

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
    def socket(self) -> Socket:
        return Socket.instance()

    @fixture
    def client(self, app: Puft) -> FlaskClient:
        return app.test_client()

    @fixture
    def socket_client(self, app: Puft, socket: Socket) -> SocketIOTestClient:
        # https://github.com/miguelgrinberg/Flask-SocketIO/blob/main/test_socketio.py
        return socket.get_test_client()

    @fixture
    def root_dir(self) -> str:
        return get_root_dir()
