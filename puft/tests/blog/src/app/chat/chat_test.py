from typing import Any
from flask_socketio import SocketIOTestClient
from pytest import fixture
from puft import Test, log, Sock


class TestChatSock(Test):
    def test_connect(self, sock_client: SocketIOTestClient):
        sock_client.connect('/chat')
        assert sock_client.is_connected('/chat')

    def test_disconnect(self, sock_client: SocketIOTestClient):
        sock_client.connect('/chat')
        sock_client.disconnect('/chat')
        # TODO

    def test_send_message(self, sock: Sock, sock_client: SocketIOTestClient):
        sock_client.connect('/chat')
        sock.emit(
            'message',
            {'message': {
                'user_author_id': 2,
                'content': 'Hello!'
            }},
            namespace='/chat')
        received_data = sock_client.get_received('/chat')

        assert \
            type(received_data) is list, \
                'Received data should have list type'
        assert \
            len(received_data) == 1, \
                'Received data should contain only one element within list'

        event: str = received_data[0]['name']
        data: dict[str, dict[str, str | int]] = received_data[0]['args']
        namespace: str = received_data[0]['namespace']

        assert type(event) is str
        assert event == 'message'

        assert type(data) is dict
        assert 'message' in data
        assert 'user_author_id' in data['message']
        assert type(data['message']['user_author_id']) is int
        assert 'content' in data['message']
        assert type(data['message']['content']) is str

        assert type(namespace) is str
        assert namespace == '/chat'
