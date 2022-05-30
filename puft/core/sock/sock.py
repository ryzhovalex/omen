from typing import TYPE_CHECKING

from flask_socketio import (
    SocketIO, send, emit, join_room, leave_room)

from puft.core.service import Service

if TYPE_CHECKING:
    from puft.core.app.puft import Puft


class Sock(Service):
    def __init__(self, config: dict, app: 'Puft') -> None:
        super().__init__(config)
        self.socket: SocketIO = SocketIO(app.get_native_app())

    def register_event_cell(self)


