from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING, Type, Sequence, TypeVar

from warepy import logger, format_message, join_paths, load_yaml

if TYPE_CHECKING:
    # Import at type checking with future.annotations to avoid circular imports and use just for typehints.
    from ..services.puft import Puft
    from ...ui.controllers.puft_controller import PuftController
    from ..services.database import Database, native_db
    from ...ui.controllers.database_controller import DatabaseController
    from ...ui.views.view import View
    from ...ui.emitters.emitter import Emitter
    from ..mappers.mapper import Mapper
    from ..services.service import Service
    from ...ui.controllers.controller import Controller
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
    def find_by_name(cells: Sequence[AnyNamedCell], name: str) -> AnyNamedCell:
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

    @staticmethod
    def parse(config_cell: ConfigCell, root_path: str, update_with: dict = None) -> dict:
        """Parse given config cell and return configuration dictionary.
        
        NOTE: This function performs automatic path absolutize - all paths starting with "./" within config 
        will be joined to given root path.

        Args:
            config_cell: Configuration cell to parse from.
            root_path: Path to join config cell source with.
            update_with (optional): dictionary to update config cell mapping with. Defaults to None.
        
        Raise:
            ValueError: If given config cell has non-relative source path.
            ValueError: If given config cell's source has unrecognized extension."""
        config = {}
        config_path = join_paths(root_path, config_cell.source)

        if config_cell.source[0] != "." and config_cell.source[1] != "/":
            error_message = format_message("Given config cell has non-relative source path {}", config_cell.source)
            raise ValueError(error_message)

        # Fetch config's extension.
        if "json" in config_path[-5:len(config_path)]:
            with open(config_path, "r") as config_file:
                config = json.load(config_file)
        elif "yaml" in config_path[-5:len(config_path)]:
            config = load_yaml(config_path)
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
class InjectionCell(NamedCell):
    """Crucial core dependency injection cell united Controller and Service objects in one chain."""
    controller_class: Type[Controller]
    service_class: Type[Service]


@dataclass
class PuftInjectionCell(InjectionCell):
    """Injection cell with app itself which is required in any build."""
    controller_class: Type[PuftController]
    service_class: Type[Puft]
    mode_enum: CLIModeEnumUnion
    host: str
    port: int


@dataclass
class DatabaseInjectionCell(InjectionCell):
    """Injection cell with database itself which can be applied to created application."""
    controller_class: Type[DatabaseController]
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