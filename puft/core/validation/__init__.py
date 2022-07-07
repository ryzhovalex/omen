from typing import Any
from enum import EnumMeta
from puft.tools.log import log
from puft.core.validation.validation_error import ValidationError


def validate(
        obj: Any, expected_type: type | list[type],
        obj_name: str = 'Entity', strict: bool = False) -> None:
    if isinstance(expected_type, type):
        if strict:
            if type(obj) is not expected_type:
                raise ValidationError(obj_name, expected_type)
        else:
            if not isinstance(obj, expected_type):
                raise ValidationError(obj_name, expected_type)
    elif type(expected_type) is list:
        found: bool = False

        for type_ in expected_type:
            if type(obj) is type_:
                found = True
        
        if not found:
            raise ValidationError(obj_name, expected_type)
    else:
        raise TypeError('Expected type should be `type` type')
