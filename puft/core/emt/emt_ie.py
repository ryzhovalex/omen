from dataclasses import dataclass

from puft.core.ie.ie import Ie

from .emt import Emt


@dataclass
class EmtIe(Ie):
    emt_class: type[Emt]