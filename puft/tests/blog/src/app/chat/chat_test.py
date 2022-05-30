from flask_socketio import SocketIOTestClient
from pytest import fixture
from puft import Test, log


class TestChat(Test):
    def test_connect(self, sock_client: SocketIOTestClient):
        assert sock_client.is_connected()

    def test_disconnect(self, sock_client: SocketIOTestClient):
        sock_client.disconnect()
        # TODO

    def test_send_message(self, sock_client: SocketIOTestClient):
        sock_client.send('Hello!')
        received = sock_client.get_received()
        log.debug(received)
        assert False
