"""Module with constants and typehints."""
from typing import Any, List, Dict, Tuple, Union, Callable, Literal


HttpMethod = Literal["GET", "POST", "PUT", "DELETE"]
HTTP_METHODS = HttpMethod.__args__

ConfigLoadType = Literal["json", "map"]
CONFIG_LOAD_TYPES = ConfigLoadType.__args__

TurboAction = Literal["append", "prepend", "replace", "update", "remove"]
TURBO_ACTIONS = TurboAction.__args__