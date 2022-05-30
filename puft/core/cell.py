from __future__ import annotations
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING, Callable, Type, Sequence, TypeVar


from puft.core.app.app_mode_enum import AppModeEnum
from .assembler.config_extension_enum import ConfigExtensionEnum

if TYPE_CHECKING:
    from puft.core.app.puft import Puft
    from puft.core.sock.sock import Sock
    from puft.core.error import Error
    from puft.core.db.db import Db
    from puft.core.view import View
    from puft.core.emitter import Emitter
    from puft.core.service import Service
    from puft.tools.hints import CLIModeEnumUnion




@dataclass
class Cell:
    pass


@dataclass
class PuftServiceCell(ServiceCell):
    """Injection cell with app itself which is required in any build."""
    service_class: type[Puft]
    mode_enum: CLIModeEnumUnion
    host: str
    port: int
    ctx_processor_func: Callable | None = None
    each_request_func: Callable | None = None
    first_request_func: Callable | None = None


@dataclass
class DbServiceCell(ServiceCell):
    """Injection cell with Db itself which can be applied to created
    application.
    """
    service_class: Type[Db]


@dataclass
class SockServiceCell(ServiceCell):
    service_class: type[Sock]


@dataclass
class ViewCell(Cell):
    endpoint: str
    view_class: type[View]
    route: str  # Route will be the same for all methods.


@dataclass
class EmitterCell(Cell):
    emitter_class: type[Emitter]


@dataclass
class ErrorCell(Cell):
    error_class: type[Error]
    handler_function: Callable
