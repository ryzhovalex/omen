from warepy import get_enum_values, get_union_enum_values

from .enums import (
    CLIDatabaseMode, CLIRunMode, CLIConstructMode, HTTPMethodName, TurboActionToken
)

CLI_DATABASE_MODES = get_enum_values(CLIDatabaseMode)
CLI_RUN_MODES = get_enum_values(CLIRunMode)
CLI_CONSTRUCT_MODES = get_enum_values(CLIConstructMode)
#
CLIModeUnion = CLIDatabaseMode | CLIRunMode | CLIConstructMode
CLI_MODES = get_union_enum_values(CLIModeUnion)

HTTP_METHODS = get_enum_values(HTTPMethodName)

TURBO_ACTIONS = get_enum_values(TurboActionToken)