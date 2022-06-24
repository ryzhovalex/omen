from dataclasses import dataclass

from core.cell.named_cell import NamedCell
from core.sv.sv import Sv


@dataclass
class SvCell(NamedCell):
    sv_class: type[Sv]
