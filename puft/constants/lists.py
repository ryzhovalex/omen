from warepy import get_enum_values, get_union_enum_values

from .enums import (
    CLIDatabaseEnum, CLIRunEnum, CLIHelperEnum, HTTPMethodEnum, TurboActionEnum
)
from .hints import (
    CLIModeEnumUnion
)

CLI_DATABASE_ENUM_VALUES = get_enum_values(CLIDatabaseEnum)  # type: list[str]
CLI_RUN_ENUM_VALUES = get_enum_values(CLIRunEnum)  # type: list[str] 
CLI_HELPER_ENUM_VALUES = get_enum_values(CLIHelperEnum)  # type: list[str]
CLI_MODE_ENUM_VALUES = get_union_enum_values(CLIModeEnumUnion)  # type: list[str]

HTTP_METHOD_ENUM_VALUES = get_enum_values(HTTPMethodEnum)  # type: list[str]

TURBO_ACTION_ENUM_VALUES = get_enum_values(TurboActionEnum)  # type: list[str]
