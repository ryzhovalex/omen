from typing import Callable
from dataclasses import dataclass

from puft.core.ie.ie import Ie

from .error import Error


@dataclass
class ErrorIe(Ie):
    error_class: type[Error]
    handler_function: Callable