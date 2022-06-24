from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass

from core.sv.sv_cell import SvCell

if TYPE_CHECKING:
    from core.sock.socket import Socket


@dataclass
class SocketSvCell(SvCell):
    sv_class: type[Socket]
