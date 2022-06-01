from typing import Any
from flask_socketio import SocketIOTestClient
from pytest import fixture
from puft import Test, log, Socket, Puft


class TestChatSock(Test):
    def test_connect(self, socket_client: SocketIOTestClient):
        socket_client.connect('/chat')
        assert socket_client.is_connected('/chat')

    def test_disconnect(self, socket_client: SocketIOTestClient):
        socket_client.connect('/chat')
        socket_client.disconnect('/chat')
        # TODO

    def test_send_message(
            self, socket: Socket, socket_client: SocketIOTestClient):
        socket_client.connect('/chat')
        socket_client.emit(
            'send',
            {'number': 1234},
            namespace='/chat')
        received_data = socket_client.get_received('/chat')

        assert type(received_data) is list
        assert len(received_data) == 1

        event: str = received_data[0]['name']
        data: dict[str, dict[str, str | int]] = received_data[0]['args']
        namespace: str = received_data[0]['namespace']

        assert event == 'message'
        assert type(data) is dict
        assert data['number'] == 4321
        assert namespace == '/chat'
