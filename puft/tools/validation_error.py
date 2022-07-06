from typing import Any
from puft.core.error.error import Error


class ValidationError(Error):
    def __init__(
            self, validated_name: str, expected_type: type | list[type],
            message: str = '', status_code: int = 400) -> None:
        if message == '':
            if isinstance(expected_type, type):
                message = \
                    f'{validated_name} should have type:' \
                    f' {expected_type.__name__}'
            elif type(expected_type) is list:
                message = \
                    f'{validated_name} should have one type of the following' \
                    f' list: {[type_.__name__ for type_ in expected_type]}'
            else:
                raise TypeError('Unrecognized type of `expected_type`')
            
        super().__init__(message, status_code)
