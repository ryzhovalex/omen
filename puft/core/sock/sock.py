from typing import TYPE_CHECKING

from flask_socketio import (
    SocketIO, send, emit, join_room, leave_room, SocketIOTestClient)

from puft.core.sv.sv import Sv

if TYPE_CHECKING:
    from puft.core.app.puft import Puft


class Sock(Sv):
    def __init__(self, config: dict, app: 'Puft') -> None:
        super().__init__(config)
        self.app = app
        self.socket: SocketIO = SocketIO(self.app.get_native_app())

    def test_client(self,) -> SocketIOTestClient:
        return self.socket.test_client(self.app.get_native_app())

    def register_event_cell(self):
        pass
