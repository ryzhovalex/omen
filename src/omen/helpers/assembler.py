from __future__ import annotations

import os
import json
from typing import Dict, Any, List, Literal, Tuple, Callable, Union, TYPE_CHECKING

from flask import Flask

from .logger import logger
from .helper import Helper
from .constants import Path
from ..tools.regular import join_paths, format_error_message, parse_config_cell
from .cells import Cell, EmitterCell, MapperCell, InjectionCell, ViewCell, ConfigCell

if TYPE_CHECKING:
    from .builder import Builder
    from ..models.domains.omen import Omen
    from ..ui.controllers.omen_controller import OmenController


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
        self.app_controller = None
        self.extra_configs_by_name = {}  # Do not set this to None at initialization, because `get()` method called from this dictionary.
        self.root_path = build.root_path
        self.config_cells_by_name = build.config_cells_by_name

        self.injection_cells_by_name = build.injection_cells_by_name
        self.mapper_cells_by_name = build.mapper_cells_by_name
        self.view_cells_by_name = build.view_cells_by_name
        self.emitter_cells_by_name = build.emitter_cells_by_name

    @staticmethod
    @logger.catch
    def create_app(configs_by_name: Dict[str, dict] = None, root_path: str = None) -> Flask:
        """Initialize Flask app with assembler build context and return this app.
        
        Reassign assembler's attributes to given ones and run it's setup operations to assemble app and other project's instances.

        Args:
            configs_by_name (optional):
                Configs to be appended to appropriate ones described in Build class. Defaults to None.
                Contain config name as key and configuration mapping as value, e.g.:
        ```
                    configs_by_name = {
                        "app": {"TESTING": True},
                        "database": {"db_uri": "sqlite3:///:memory:"}
                    }
        ```
            root_path (optional):
                Root path to execute project from. Defaults to `os.getcwd()`.
                Required in cases of calling this function not from actual project root (e.g. from tests) to set root path explicitly.
        """
        assembler = Assembler()  # Get Assembler instance without args, because it should be initialized before (in root create_app function).

        if root_path:
            assembler.root_path = root_path
        if configs_by_name:
            assembler.extra_configs_by_name = configs_by_name

        assembler._build_all()
        flask_app = assembler.app.get_app()

        return flask_app
        
    @logger.catch
    def _build_all(self) -> None:
        """Send commands to build all given instances."""
        # Set root path environ for various usage within project.
        os.environ["ROOT_PATH"] = self.root_path

        # Build instances by key groups.
        if "logger" in self.config_cells_by_name.keys():
            logger_config = parse_config_cell(
                config_cell=self.config_cells_by_name["logger"], 
                root_path=self.root_path, 
                update_with=self.extra_configs_by_name.get("logger", None)
            )
        else:
            logger_config = None
        self._build_logger(config=logger_config)

        # Call command to build injections.
        if self.injection_cells_by_name:
            self._build_injection(injection_cells_by_name=self.injection_cells_by_name)
        elif not "app" in self.injection_cells_by_name:
            error_message = format_error_message(
                "App injection cell with token `app` should have been given at minimum."
            )
            raise TypeError(error_message)

        # Build views.
        if self.view_cells_by_name:
            self._build_views(view_cells=list(self.view_cells_by_name.values()))

        # Build mappers.
        if self.mapper_cells_by_name:
            self._build_mappers(mapper_cells=list(self.mapper_cells_by_name.values()))

        # Build Emitters with Omen injection.
        if self.emitter_cells_by_name:
            self._build_emitters(emitter_cells=list(self.emitter_cells_by_name.values()))

    @logger.catch
    def _build_logger(self, config: dict = None) -> None:
        """Build logger with given config.
        
        If config is None, build with default parameters."""
        # Use full or partially (with replacing missing keys from default) given config.
        logger_kwargs = self.DEFAULT_LOGGER_PARAMS
        if config:
            for k, v in config.items():
                logger_kwargs[k] = v
        logger.init_logger(**logger_kwargs)

    @logger.catch
    def _build_injection(self, injection_cells_by_name: Dict[str, InjectionCell]) -> None:
        """Setup all injection instances: Controllers, Services and Domain Objects in 1:1:1 relation."""
        def _run_injection_cells(injection_cells: List[InjectionCell]) -> None:
            """Unpack injection cells with loop and init Service, by inject Domain, and Controller, by inject Service.
            
            Add config to cell's kwargs for domain, if one with the same name specified (e.g. you have config cell with name "app" and 
            injections cell with name "app" => domain "app" will receive configuration map from config cell."""
            for cell in injection_cells:
                domain_kwargs = cell.domain_kwargs
                # Check for domain's config in given cells by comparing names.
                if cell.name in self.config_cells_by_name:
                    domain_kwargs["config"] = parse_config_cell(
                        root_path=self.root_path, 
                        config_cell=self.config_cells_by_name[cell.name],
                        update_with=self.extra_configs_by_name.get(cell.name, None)
                    )
                # Fetch project version from info.json from the root path. 
                if cell.name == "app":
                    with open(join_paths(self.root_path, "./info.json")) as info_file:
                        info_data = json.load(info_file)
                        try:
                            domain_kwargs["project_version"] = info_data["version"]
                        except KeyError:
                            error_message =  format_error_message("Project version is not specified in `info.json` file.")
                            raise KeyError(error_message)

                cell.service_class(service_kwargs=cell.service_kwargs, domain_class=cell.domain_class, domain_kwargs=domain_kwargs)
                cell.controller_class(controller_kwargs=cell.service_kwargs, service_class=cell.service_class)

        _run_injection_cells(list(injection_cells_by_name.values()))

        # Assign app to use within assembler.
        self.app = injection_cells_by_name["app"].domain_class()  # type: Omen
        # Assign app controller mainly to be used as injection for emitters.
        self.app_controller = injection_cells_by_name["app"].controller_class()  # type: OmenController

        # Check if database given as service cell and perform it's postponed setup.
        # Postponed setup is required, because Database uses Flask app to init native SQLAlchemy db inside, 
        # so it's possible only after App initialization.
        if "database" in injection_cells_by_name:
            injection_cells_by_name["database"].domain_class().setup_db(flask_app=self.get_flask_app())

        # Call postponed build from created App.
        try:
            self.app.postbuild()
        except NotImplementedError:
            pass

    @logger.catch
    def _build_views(self, view_cells: List[ViewCell]) -> None:
        """Build all views by registering them to app."""
        for view_cell in view_cells:
            self.app.register_view(view_cell)

    @staticmethod
    @logger.catch
    def _build_mappers(mapper_cells: List[MapperCell]) -> None:
        """Assign models parameters to mapper classes."""
        for cell in mapper_cells:
            cell.mapper_class.model = cell.model
            cell.mapper_class.params = cell.mapper_kwargs

    @logger.catch
    def _build_emitters(self, emitter_cells: List[EmitterCell]) -> None:
        """Build emitters from given cells and inject Omen application controllers to each."""
        for cell in emitter_cells:
            cell.emitter_class(app_controller=self.app_controller)