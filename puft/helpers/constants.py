"""Module with constants and typehints."""
from typing import Any, List, Dict, Tuple, Union, Callable, Literal, get_args

from puft.models.domains.puft import Puft


PuftDatabaseMode = Literal["init", "migrate", "upgrade"]
PUFT_DATABASE_MODES = get_args(PuftDatabaseMode)
#
PuftRunMode = Literal["dev", "prod", "test"]
PUFT_RUN_MODES = get_args(PuftRunMode)
#
PuftConstructMode = Literal["deploy"]
PUFT_CONSTRUCT_MODES = get_args(PuftConstructMode)
#
PuftMode = Union[PuftDatabaseMode, PuftRunMode, PuftConstructMode]
PUFT_MODES = PUFT_DATABASE_MODES + PUFT_RUN_MODES + PUFT_CONSTRUCT_MODES

HttpMethod = Literal["GET", "POST", "PUT", "DELETE"]
HTTP_METHODS = get_args(HttpMethod)

TurboAction = Literal["append", "prepend", "replace", "update", "remove"]
TURBO_ACTIONS = get_args(TurboAction)
