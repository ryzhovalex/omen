from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Dict, Union, Callable, Literal, TYPE_CHECKING, Type

if TYPE_CHECKING:
    # Import at type checking with future.annotations to avoid circular imports and use just for typehints.
    from ..models.domains.puft import Puft
    from ..models.domains.database import Database
    from ..models.services.puft_service import PuftService
    from ..ui.controllers.puft_controller import PuftController
    from ..models.services.database_service import DatabaseService
    from ..ui.controllers.database_controller import DatabaseController

    from ..ui.views.view import View
    from ..models.domains.database import native_db
    from ..ui.emitters.emitter import Emitter
    from ..models.mappers.mapper import Mapper
    from ..models.domains.domain import Domain
    from ..models.services.service import Service
    from ..ui.controllers.controller import Controller


@dataclass
class Cell:
    name: str


@dataclass
class ConfigCell(Cell):
    """Config cell which can be used to load configs to appropriate instance's configuration by name."""
    source: str


@dataclass
class InjectionCell(Cell):
    """Crucial core dependency injection cell united Controller, Service and Domain object in one chain."""
    controller_class: Type[Controller]
    controller_kwargs: Dict[str, Any]
    service_class: Type[Service]
    service_kwargs: Dict[str, Any]
    domain_class: Type[Domain]
    domain_kwargs: Dict[str, Any]


@dataclass
class AppInjectionCell(InjectionCell):
    """Injection cell with app itself which is required in any build."""
    controller_class: Type[PuftController]
    service_class: Type[PuftService]
    domain_class: Type[Puft]

@dataclass
class DatabaseInjectionCell(InjectionCell):
    """Injection cell with database itself which can be applied to created application."""
    controller_class: Type[DatabaseController]
    service_class: Type[DatabaseService]
    domain_class: Type[Database]


@dataclass
class MapperCell(Cell):
    mapper_class: Type[Mapper]
    model: Type[native_db.Model]
    mapper_kwargs: Dict[str, Any]


@dataclass
class ViewCell(Cell):
    name: str  # `name` == view's final endpoint, e.g. `objective.basic`.
    view_class: Type[View]
    view_kwargs: Dict[str, Any]
    route: str  # Route will be the same for all methods.


@dataclass
class EmitterCell(Cell):
    emitter_class: Type[Emitter]