"""Module with constants and typehints."""
from typing import Any, List, Dict, Tuple, Union, Callable, Literal


Modes = Literal["dev", "prod", "test", "init", "migrate", "upgrade"]
MODES = Modes.__args__

HttpMethod = Literal["GET", "POST", "PUT", "DELETE"]
HTTP_METHODS = HttpMethod.__args__

TurboAction = Literal["append", "prepend", "replace", "update", "remove"]
TURBO_ACTIONS = TurboAction.__args__
