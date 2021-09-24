from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Dict, Union, Callable, Literal, TYPE_CHECKING

from .constants import TurboName, ConfigLoadType, Path

if TYPE_CHECKING:
    # Import at type checking with future.annotations to avoid circular imports and use just for typehints.
    from ..ui.views.view import View
    from ..models.domains.database import db
    from ..models.mappers.mapper import Mapper
    from ..models.domains.domain import Domain
    from ..models.services.service import Service
    from ..ui.controllers.controller import Controller


@dataclass
class Cell:
    name: str


@dataclass
class ConfigCell(Cell):
    """Config cell which can be used to load maps or json files to appropriate instance's configuration by name."""
    load_type: ConfigLoadType
    source: Union[Path, dict]


@dataclass
class InjectionCell(Cell):
    """Crucial core dependency injection cell united Controller, Service and Domain object in one chain."""
    controller_class: Controller
    controller_kwargs: Dict[str, Any]
    service_class: Service
    service_kwargs: Dict[str, Any]
    domain_class: Domain
    domain_kwargs: Dict[str, Any]


@dataclass
class MapperCell(Cell):
    mapper_class: Mapper
    model: db.Model
    mapper_kwargs: Dict[str, Any]


@dataclass
class ViewCell(Cell):
    name: str  # `name` == view's final endpoint, e.g. `objective.basic`.
    view_class: View
    view_kwargs: Dict[str, Any]
    route: str  # Route will be the same for all methods.


@dataclass
class TurboCell(Cell):
    name: str
    template_path: str  # Path relative to 'templates' folder, e.g. "home/turbo-weather.html"
    target_id: str  # Id of target element within the template, e.g. "turbo-weather"