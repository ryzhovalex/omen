__version__ = "0.0.0"

from puft import (
    Build, SvCell, ViewCell, SockHandlerCell)

from src.app.user.user_sv import UserSv
from src.tools.shell import import_main, import_std
from src.app.user.user_view import UserView
from src.app.chat.chat_sv import ChatSv
from puft.tests.blog.src.app.chat.chat_sock_handler import ChatSockHandler


sv_cells: list[SvCell] = [
    SvCell('user', UserSv),
    SvCell('chat', sv_class=ChatSv)
]

sock_handler_cells: list[SockHandlerCell] = [
    SockHandlerCell('/chat', ChatSockHandler)
]


view_cells: list[ViewCell] = [
    ViewCell('user', UserView, '/user/<int:id>')
]


build = Build(
    version=__version__,
    sv_cells=sv_cells,
    view_cells=view_cells,
    shell_processors=[import_std, import_main])
