from puft.core.error.error import Error
from puft.core.validation import validate


class ParsingError(Error):
    pass


class IntParsingError(ParsingError):
    def __init__(
            self,
            parsed_str: str,
            message: str = '',
            status_code: int = 400) -> None:
        validate(parsed_str, str, 'Parsed str')
        if message == '':
            message = f'{parsed_str} is not parseable to int'
        super().__init__(message, status_code)
        

class KeyParsingError(ParsingError):
    def __init__(
            self,
            parsed_map: dict,
            failed_key: str,
            message: str = '',
            status_code: int = 400) -> None:
        validate(parsed_map, dict, 'Parsed map')
        validate(failed_key, str, 'Failed key')

        if message == '':
            message = f'{parsed_map} has no key: \'{failed_key}\''
        super().__init__(message, status_code)
