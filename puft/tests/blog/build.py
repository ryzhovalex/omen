__version__ = "0.0.0"

from puft import (
    Build, SvIe, ViewIe, SockIe)

from src.app.user.user_sv import UserSv
from src.tools.shell import import_main, import_std
from src.app.user.user_view import UserView
from src.app.chat.chat_sv import ChatSv
from puft.tests.blog.src.app.chat.chat_sock import ChatSock


sv_ies: list[SvIe] = [
    SvIe('user', UserSv),
    SvIe('chat', sv_class=ChatSv)
]

sock_ies: list[SockIe] = [
    SockIe('/chat', ChatSock)
]


view_ies: list[ViewIe] = [
    ViewIe('user', UserView, '/user/<int:id>')
]


build = Build(
    version=__version__,
    sv_ies=sv_ies,
    view_ies=view_ies,
    shell_processors=[import_std, import_main],
    sock_ies=sock_ies)
