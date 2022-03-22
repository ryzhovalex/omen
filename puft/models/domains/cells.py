from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING, Type, Sequence, TypeVar

from warepy import log, format_message, join_paths, load_yaml

if TYPE_CHECKING:
    # Import at type checking with future.annotations to avoid circular imports and use just for typehints.
    from ..services.puft import Puft
    from ..services.database import Database, native_db
    from ...views.view import View
    from ...emitters.emitter import Emitter
    from ..mappers.mapper import Mapper
    from ..services.service import Service
    from ...constants.hints import CLIModeEnumUnion


# Set TypeVar upper bound to class defined afterwards.
# https://stackoverflow.com/questions/63830289/setting-typevar-upper-bound-to-class-defined-afterwards
AnyNamedCell = TypeVar("AnyNamedCell", bound="NamedCell")


@dataclass
class Cell:
    pass


@dataclass
class NamedCell(Cell):
    name: str

    @staticmethod
    def find_by_name(name: str, cells: Sequence[AnyNamedCell]) -> AnyNamedCell:
        """Traverse through given list of cells and return first one with specified name.
        
        raise:
            ValueError: 
                No cell with given name found.
        """
        for cell in cells:
            if cell.name == name:
                return cell
        raise ValueError(format_message("No cell with given name {} found.", name))

    @staticmethod
    def map_to_name(cells: list[AnyNamedCell]) -> dict[str, AnyNamedCell]:
        """Traverse through given cells names and return dict with these cells as values and their names as keys."""
        cells_by_name = {}
        for cell in cells:
            cells_by_name[cell.name] = cell
        return cells_by_name


@dataclass
class ConfigCell(NamedCell):
    """Config cell which can be used to load configs to appropriate instance's configuration by name."""
    source: str

    def parse(self, root_path: str, update_with: dict = None) -> dict:
        """Parse config cell and return configuration dictionary.

        Args:
            config_cell: Configuration cell to parse from.
            root_path: Path to join config cell source with.
            update_with (optional): dictionary to update config cell mapping with. Defaults to None.
        
        Raise:
            ValueError: If given config cell's source has unrecognized extension.
        """
        config = {}

        # Fetch config's extension.
        if "json" in self.source[-5:len(self.source)]:
            with open(self.source, "r") as config_file:
                config = json.load(config_file)
        elif "yaml" in self.source[-5:len(self.source)]:
            config = load_yaml(self.source)
        else:
            error_message = format_message("Unrecognized config cell source's extension.")
            raise ValueError(error_message)

        # Traverse all values and find paths required to be joined to the root path.
        for k, v in config.items():
            if type(v) == str:
                if v[0] == "." and v[1] == "/":
                    config[k] = join_paths(root_path, v)

        # Update given config with extra dictionary if this dictionary given and not empty.
        if update_with:
            config.update(update_with)

        return config


@dataclass
class ServiceCell(NamedCell):
    service_class: Type[Service]


@dataclass
class PuftServiceCell(ServiceCell):
    """Injection cell with app itself which is required in any build."""
    service_class: Type[Puft]
    mode_enum: CLIModeEnumUnion
    host: str
    port: int


@dataclass
class DatabaseServiceCell(ServiceCell):
    """Injection cell with database itself which can be applied to created application."""
    service_class: Type[Database]


@dataclass
class MapperCell(NamedCell):
    mapper_class: Type[Mapper]
    model: Type[native_db.Model]


@dataclass
class ViewCell(NamedCell):
    # `name` == view's final endpoint, e.g. `objective.basic`.
    view_class: Type[View]
    route: str  # Route will be the same for all methods.


@dataclass
class EmitterCell(NamedCell):
    emitter_class: Type[Emitter]
