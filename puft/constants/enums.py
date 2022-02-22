"""Module with constants and typehints."""
from typing import Any, List, Dict, Tuple, Union, Callable, Literal, get_args
from enum import Enum


class CLIDatabaseMode(Enum):
    INIT = "init"
    MIGRATE = "migrate"
    UPGRADE = "upgrade"


class CLIRunMode(Enum):
    DEV = "dev"
    PROD = "prod"
    TEST = "test"


class CLIConstructMode(Enum):
    DEPLOY = "deploy"


class HTTPMethodName(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class TurboActionToken(Enum):
    APPEND = "append"
    PREPEND = "prepend"
    REPLACE = "replace"
    UPDATE = "update"
    REMOVE = "remove"

