from __future__ import annotations

import re
import os
import json
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING, Callable, Type, Sequence, TypeVar

from flask_sqlalchemy import SQLAlchemy
from warepy import get_enum_values, log, format_message, join_paths, load_yaml

from puft.constants.enums import AppModeEnum, ConfigExtensionEnum

if TYPE_CHECKING:
    # Import at type checking with future.annotations to avoid circular imports
    # and use just for typehints.
    from ..services.puft import Puft
    from ..services.database import Database
    from ...views.view import View
    from ...emitters.emitter import Emitter
    from ..mappers.mapper import Mapper
    from ..services.service import Service
    from ...constants.hints import CLIModeEnumUnion


# Set TypeVar upper bound to class defined afterwards.
# https://stackoverflow.com/a/67662276
AnyNamedCell = TypeVar("AnyNamedCell", bound="NamedCell")


@dataclass
class Cell:
    pass


@dataclass
class NamedCell(Cell):
    name: str

    @staticmethod
    def find_by_name(name: str, cells: Sequence[AnyNamedCell]) -> AnyNamedCell:
        """Traverse through given list of cells and return first one with
        specified name.
        
        Raise:
            ValueError: 
                No cell with given name found.
        """
        for cell in cells:
            if cell.name == name:
                return cell
        raise ValueError(format_message("No cell with given name {} found.", name))

    @staticmethod
    def map_to_name(cells: list[AnyNamedCell]) -> dict[str, AnyNamedCell]:
        """Traverse through given cells names and return dict with these cells
        as values and their names as keys."""
        cells_by_name: dict[str, AnyNamedCell] = {}
        for cell in cells:
            cells_by_name[cell.name] = cell
        return cells_by_name


@dataclass
class ConfigCell(NamedCell):
    """Config cell which can be used to load configs to appropriate instance's
    configuration by name."""
    source_by_app_mode: dict[AppModeEnum, str]

    def parse(
            self, app_mode_enum: AppModeEnum, root_path: str,
            update_with: dict[str, Any] | None = None,
            convert_keys_to_lower: bool = True) -> dict[str, Any]:
        """Parse config cell and return configuration dictionary.

        Args:
            app_mode_enum:
                App mode to run appropriate config.
            root_path:
                Path to join config cell source with.
            update_with (optional):
                Dictionary to update config cell mapping with.
                Defaults to None.
            convert_keys_to_lower (optional):
                If true, all keys from origin mapping and mapping from
                `update_with` will be converted to upper case.
        
        Raise:
            ValueError:
                If given config cell's source has unrecognized extension.
        """
        config: dict[str, Any] = {}
        if app_mode_enum in self.source_by_app_mode:
            source = self.source_by_app_mode[app_mode_enum]
        else:
            # Apply searching strategy: test -> dev -> prod.
            if app_mode_enum is AppModeEnum.TEST:
                if AppModeEnum.DEV in self.source_by_app_mode:
                    source = self.source_by_app_mode[AppModeEnum.DEV]
                else:
                    source = self.source_by_app_mode[AppModeEnum.PROD]
            elif app_mode_enum is AppModeEnum.DEV:
                source = self.source_by_app_mode[AppModeEnum.PROD]
            else:
                raise
                    
        source_extension = source[source.rfind(".")+1:]
        
        # Fetch config's extension.
        match source_extension:
            case "json":
                with open(source, "r") as config_file:
                    config = json.load(config_file)
            case "yaml":
                config = load_yaml(source)
            case _:
                error_message = format_message(
                    "Unrecognized config cell source's extension.")
                raise ValueError(error_message)

        if config:
            self._parse_string_config_values(config, root_path)
        else:
            config = {}

        # Update given config with extra dictionary if this dictionary given
        # and not empty.
        if update_with:
            config.update(update_with)

        if convert_keys_to_lower:
            rconfig = {}
            for k, v in config.items():
                rconfig[k.lower()] = v
            config = rconfig

        return config
    
    def _parse_string_config_values(
            self, config: dict[str, Any], root_path: str) -> None:
        for k, v in config.items():
            if type(v) == str:
                # Find environs to be requested.
                # Exclude escaped curly braces like `\{not_environ\}`.
                envs: list[str] = re.findall(r"[^\\]\{\w+\}", v)
                if envs:
                    for env in [
                                x.replace("{", "").replace("}", "")
                                for x in envs
                            ]:
                        env = env.strip()
                        real_env_value = os.getenv(env.strip())
                        if real_env_value is None:
                            log.debug(env == "PATH")
                            raise ValueError(
                                f"Environ {env} specified in field"
                                f" {self.name}.{k} was not found")
                        else:
                            v = v.replace("{" + f"{env}" + "}", real_env_value)

                # Look for escaped curly braces and normalize them.
                v = v.replace(r"\{", "{").replace(r"\}", "}")

                # Find paths required to be joined to the root path.
                if v[0] == "." and v[1] == "/":
                    config[k] = join_paths(root_path, v)
                else:
                    config[k] = v


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
    ctx_processor_func: Callable | None = None
    each_request_func: Callable | None = None
    first_request_func: Callable | None = None


@dataclass
class DatabaseServiceCell(ServiceCell):
    """Injection cell with database itself which can be applied to created application."""
    service_class: Type[Database]


@dataclass
class MapperCell(NamedCell):
    mapper_class: Type[Mapper]
    model: Type[SQLAlchemy.Model]


@dataclass
class ViewCell(NamedCell):
    # `name` == view's final endpoint, e.g. `objective.basic`.
    view_class: Type[View]
    route: str  # Route will be the same for all methods.


@dataclass
class EmitterCell(NamedCell):
    emitter_class: Type[Emitter]
