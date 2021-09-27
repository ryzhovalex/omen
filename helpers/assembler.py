from __future__ import annotations

import os
import json
from typing import Dict, Any, List, Literal, Tuple, Callable, Union, TYPE_CHECKING

from flask import Flask

from .logger import logger
from .helper import Helper
from .constants import Path
from ..tools.stdkit import join_paths, format_error_message, parse_config_cell, make_abs_path_for_config_cells
from .cells import Cell, MapperCell, InjectionCell, TurboCell, ViewCell, ConfigCell

if TYPE_CHECKING:
    from ..models.domains.omen import Omen
    from .builder import Builder


class Assembler(Helper):
    """Assembles all project instances from given `Builder` type's class and initializes it.
    
    Acts automatically and shouldn't be inherited directly by project in any form."""
    DEFAULT_LOGGER_PARAMS = {
        "path": "./instance/logs/system/debug.log",
        "level": "DEBUG",
        "format": "{time:%Y.%m.%d at %H:%M:%S:%f%z} | {level} | {extra} >> {message}",
        "rotation": "10 MB",
        "serialize": False
    }

    def __init__(
        self, 
        build: Builder,
        *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        # Define attributes for getter methods to be used at builder.
        self.app = None
        self.module_path = build.module_path
        self.config_cells_by_name = build.config_cells_by_name
        self.db_uri = build.db_uri

        self.injection_cells_by_name = build.injection_cells_by_name
        self.mapper_cells_by_name = build.mapper_cells_by_name
        self.turbo_cells_by_name = build.turbo_cells_by_name
        self.view_cells_by_name = build.view_cells_by_name

    def get_flask_app(self) -> Flask:
        """Return Flask App model."""
        return self.app.get_app()

    def get_db_uri(self) -> Path:
        """Return db uri.
        
        Raise:
            TypeError: If db uri is None or empty path."""
        if not self.db_uri:
            error_message = format_error_message("Requested database uri is None or empty path.")
            raise TypeError(error_message)
        else:
            return self.db_uri
        
    def extend_config_cells(self, config_cells: List[ConfigCell]) -> None:
        """Extend and redefined existing configuration cells."""
        for cell in config_cells:
            self.config_cells_by_name[cell.name] = cell

        
    @staticmethod
    @logger.head_catch
    def create_app(config_cells: List[ConfigCell] = None, db_uri: str = None, module_path: str = None) -> Flask:
        """Initialize Flask app with assembler build context and return this app.
        
        Reassign assembler's attributes to given ones and run it's setup operations to assemble app and other project's instances."""
        assembler = Assembler()  # Get Assembler instance without args, because it should be initialized before (in root create_app function).

        if db_uri:
            assembler.db_uri = db_uri
        if module_path:
            assembler.module_path = module_path
        if config_cells:
            assembler.extend_config_cells(config_cells=config_cells)

        assembler.build_all()
        flask_app = assembler.get_flask_app()

        return flask_app

    @logger.head_catch
    def build_all(self) -> None:
        """Send commands to build all given instances."""
        # Make all json config cell's paths to absolute.
        make_abs_path_for_config_cells(config_cells_by_name=self.config_cells_by_name, root_path=self.module_path)
        # Build instances by key groups.
        if "logger" in self.config_cells_by_name.keys():
            logger_config = parse_config_cell(config_cell=self.config_cells_by_name["logger"])
        else:
            logger_config = None
        self._build_logger(config=logger_config)

        if self.injection_cells_by_name:
            self._build_injection(injection_cells_by_name=self.injection_cells_by_name)
        elif not self.injection_cells_by_name or not "app" in self.injection_cells_by_name:
            error_message = format_error_message(
                "Empty or None injection cells has been given. App injection cell with token `app` should have been given at minimum."
            )
            raise TypeError(error_message)

        if self.view_cells_by_name:
            self._build_views(view_cells_by_name=self.view_cells_by_name)

        if self.mapper_cells_by_name:
            self._build_mappers(mapper_cells=list(self.mapper_cells_by_name.values()))

    @logger.head_catch
    def _build_logger(self, config: dict = None) -> None:
        """Build logger with given config.
        
        If config is None, build with default parameters."""
        # Use full or partially (with replacing missing keys from default) given config.
        logger_kwargs = self.DEFAULT_LOGGER_PARAMS
        if config:
            for k, v in config:
                logger_kwargs[k] = v
        logger.init_logger(logger_kwargs)

    @logger.head_catch
    def _build_injection(self, injection_cells_by_name: Dict[str, InjectionCell]) -> None:
        """Setup all injection instances: Controllers, Services and Domain Objects in 1:1:1 relation."""
        def _run_injection_cells(injection_cells: List[InjectionCell]) -> None:
            """Unpack injection cells with loop and init Service, by inject Domain, and Controller, by inject Service."""
            for cell in injection_cells:
                cell.service_class(service_kwargs=cell.service_kwargs, domain_class=cell.domain_class, domain_kwargs=cell.domain_kwargs)
                cell.controller_class(controller_kwargs=cell.service_kwargs, service_class=cell.service_class)

        _run_injection_cells(list(injection_cells_by_name.values()))

        # Assign app to use within assembler.
        self.app = injection_cells_by_name["app"].domain_class()  # type: Omen

        # Check if database given as service cell and perform it's postponed setup.
        # Postponed setup is required, because Database uses Flask app to init native SQLAlchemy db inside, 
        # so it's possible only after App initialization.
        if "database" in injection_cells_by_name:
            injection_cells_by_name["database"].domain_class().setup_db(flask_app=self.get_flask_app(), db_uri=self.db_uri)

    @logger.head_catch
    def _build_views(self, view_cells_by_name: Dict[str, ViewCell]) -> None:
        """Build all views by registering them to app."""
        for view_cell in view_cells_by_name.values():
            self.app.register_view(view_cell)

    @staticmethod
    @logger.head_catch
    def _build_mappers(mapper_cells: List[MapperCell]) -> None:
        """Assign models parameters to mapper classes."""
        for cell in mapper_cells:
            cell.mapper_class.model = cell.model
            cell.mapper_class.params = cell.mapper_kwargs