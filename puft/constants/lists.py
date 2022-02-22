from warepy import get_enum_values, get_union_enum_values

from .enums import (
    CLIDatabaseMode, CLIRunMode, CLIConstructMode, HTTPMethodToken, TurboActionToken
)
from .hints import (
    CLIModeUnion
)

CLI_DATABASE_MODES = get_enum_values(CLIDatabaseMode)  # type: list[str]
CLI_RUN_MODES = get_enum_values(CLIRunMode)  # type: list[str] 
CLI_CONSTRUCT_MODES = get_enum_values(CLIConstructMode)  # type: list[str]
CLI_MODES = get_union_enum_values(CLIModeUnion)  # type: list[str]

HTTP_METHOD_TOKENS = get_enum_values(HTTPMethodToken)  # type: list[str]

TURBO_ACTION_TOKENS = get_enum_values(TurboActionToken)  # type: list[str]
