from dataclasses import dataclass

from core.cell.cell import Cell

from .view import View


@dataclass
class ViewCell(Cell):
    endpoint: str
    view_class: type[View]
    route: str  # Route will be the same for all methods.