from .enums import (
    CLIDatabaseEnum, CLIRunEnum, CLIConstructEnum, HTTPMethodEnum, TurboActionEnum
)

CLIModeUnion = CLIDatabaseEnum | CLIRunEnum | CLIConstructEnum
