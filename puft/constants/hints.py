from .enums import (
    CLIDatabaseMode, CLIRunMode, CLIConstructMode, HTTPMethodToken, TurboActionToken
)

CLIModeUnion = CLIDatabaseMode | CLIRunMode | CLIConstructMode
