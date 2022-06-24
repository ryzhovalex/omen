from dataclasses import dataclass

from puft.core.ie.ie import Ie

from .view import View


@dataclass
class ViewIe(Ie):
    endpoint: str
    view_class: type[View]
    route: str  # Route will be the same for all methods.