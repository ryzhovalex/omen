from .enums import (
    CLIDatabaseEnum, CLIRunEnum, CLIConstructEnum, HTTPMethodEnum, TurboActionEnum
)

CLIModeEnumUnion = CLIDatabaseEnum | CLIRunEnum | CLIConstructEnum
