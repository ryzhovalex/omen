__version__ = "0.0.0"

from puft import (
    Build, ServiceCell, ViewCell
)

from src.app.user.user_sv import UserSv
from src.tools.shell import import_main, import_std
from src.app.user.user_view import UserView
from src.app.chat.chat_sv import ChatSv


service_cells: list[ServiceCell] = [
    ServiceCell('user', UserSv),
    ServiceCell('chat', service_class=ChatSv)
]


view_cells: list[ViewCell] = [
    ViewCell('user', UserView, '/user/<int:id>')
]


build = Build(
    version=__version__,
    service_cells=service_cells,
    view_cells=view_cells,
    shell_processors=[import_std, import_main])
