from dataclasses import dataclass, fields
from typing import Any
import types
from puft.tools.log import log
from typing import ClassVar
from warepy import snakefy
from schema import Schema, Or, Optional


@dataclass
class Ie:
    """Basic interface dataclass."""
    FORMATTED_NAME: ClassVar[str | None] = None

    @property
    def formatted_name(self):
        return self._get_formatted_name

    def get_json(self) -> dict:
        return {
            self._get_formatted_name(): self._get_decomposed_dict()
        }

    def get_inner_json(self) -> dict:
        """Return json without header."""
        return self._get_decomposed_dict()

    def _get_decomposed_dict(self) -> dict:
        res_dict: dict = {}

        # Decompose all keys in self dict
        for k, v in self.__dict__.items():
            if type(v) is Ie:
                # For folded Ies make their own json decompositions
                res_dict[k] = v.get_inner_json()
            else:
                res_dict[k] = v

        return res_dict

    @classmethod
    def get_json_types(cls) -> dict:
        # https://stackoverflow.com/a/51953411/14748231
        return {
            cls._get_formatted_name(): {
                field.name: field.type for field in fields(cls)
            }
        }

    @classmethod
    def _get_formatted_name(cls, base_name: str = 'Ie') -> str:
        name: str

        if cls.FORMATTED_NAME:
            name = cls.FORMATTED_NAME
        else:
            name = snakefy(cls.__name__.replace(base_name, ''))

        return name

    @classmethod
    def _fetch_schema_types(cls, data: dict) -> dict:
        schema_types: dict = {}

        for k, v in data.items():
            if type(v) is dict:
                # Call self recusively if another dict encountered
                schema_types[k] = cls._fetch_schema_types(v)
            elif type(v) is types.UnionType:
                # Unpack arguments (classes) of union into schema's `Or`
                # statement
                schema_types[k] = Or(*v.__args__)
            else:
                # Others go normally
                schema_types[k] = v

        # All other keys does not matter and optional - useful for checking
        # child classes under base class calling procedure
        schema_types.update({Optional(str): object})

        return schema_types

    @classmethod
    def get_schema(cls) -> Schema:
        schema_types: dict = \
            cls._fetch_schema_types(cls.get_json_types())
        return Schema(schema_types)

    @classmethod
    def validate(cls, data: dict, **kwargs) -> None:
        cls.get_schema().validate(data, **kwargs)
