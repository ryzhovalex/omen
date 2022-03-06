from __future__ import annotations

import os
from typing import Dict, TYPE_CHECKING

from flask import Flask
from puft.constants.hints import CLIModeEnumUnion
from warepy import logger, join_paths, format_message, load_yaml

from .helper import Helper
from ..models.domains.cells import NamedCell, ConfigCell, InjectionCell, PuftInjectionCell, DatabaseInjectionCell
from ..models.services.database import Database
from ..models.services.puft import Puft
from ..ui.controllers.database_controller import DatabaseController
from ..ui.controllers.puft_controller import PuftController
from ..constants.hints import CLIModeEnumUnion

if TYPE_CHECKING:
    from .build import Build
    from ..ui.controllers.puft_controller import PuftController


class Assembler(Helper):
    """Assembles all project instances from given `Builder` type's class and initializes it.
    
    Acts automatically and shouldn't be inherited directly by project in any form."""
    DEFAULT_LOGGER_PARAMS = {
        "path": "./instance/logs/system.log",
        "level": "DEBUG",
        "format": "{time:%Y.%m.%d at %H:%M:%S:%f%z} | {level} | {extra} >> {message}",
        "rotation": "10 MB",
        "serialize": False
    }

    def __init__(
        self, 
        mode_enum: CLIModeEnumUnion, host: str, port: int,
        build: Build,
        *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        # Define attributes for getter methods to be used at builder.
        self.extra_configs_by_name = {}  # Do not set this to None at initialization, because `get()` method called from this dictionary.
        self.root_path = build.root_path
        self.config_cells = build.config_cells
        self.injection_cells = build.injection_cells
        self.mapper_cells = build.mapper_cells
        self.view_cells = build.view_cells
        self.emitter_cells = build.emitter_cells
        self.mode_enum = mode_enum
        self.shell_processors = build.shell_processors
        self.cli_cmds = build.cli_cmds

        # Set environ for given mode.
        os.environ["PUFT_MODE"] = self.mode_enum.value

        # Traverse given configs and assign enabled builtin cells.
        self._assign_builtin_injection_cells(mode_enum, host, port)

    @logger.catch
    def get_puft(self) -> Puft:
        return self.puft

    @logger.catch
    def get_database(self) -> Database:
        return self.database

    @logger.catch
    def _assign_builtin_injection_cells(self, mode_enum: CLIModeEnumUnion, host: str, port: int) -> None:
        """Assign builting injection cells if configuration file for its service exists."""
        self.builtin_injection_cells = []
        self.builtin_injection_cells.append(PuftInjectionCell(
            name="puft",
            controller_class=PuftController,
            service_class=Puft,
            mode_enum=mode_enum,
            host=host,
            port=port
        ))

        # Enable only modules with specified configs.
        if self.config_cells:
            try:
                NamedCell.find_by_name(self.config_cells, "database")
            except ValueError:
                pass
            else:
                self.builtin_injection_cells.append(DatabaseInjectionCell(
                    name="database",
                    controller_class=DatabaseController,
                    service_class=Database
                ))
                logger.info("Database layer enabled.")

    @staticmethod
    @logger.catch
    def build(
        configs_by_name: Dict[str, dict] | None = None, root_path: str | None = None
    ) -> None:
        """Initialize all given to Assembler instances in their dependencies.
        
        Reassign assembler's attributes to given ones and run it's setup operations to assemble app and other project's instances.

        Args:
            configs_by_name (optional):
                Configs to be appended to appropriate ones described in Build class. Defaults to None.
                Contain config name as key (which is compared to ConfigCell name field) and configuration mapping as value, e.g.:
        ```py
        configs_by_name = {
            "app": {"TESTING": True},
            "database": {"db_uri": "sqlite3:///:memory:"}
        }
        ```
            root_path (optional):
                Root path to execute project from. Defaults to `os.getcwd()`.
                Required in cases of calling this function not from actual project root (e.g. from tests) to set root path explicitly.
        """
        # Get Assembler instance without args, because it should be initialized before (in root create_app function).
        assembler = Assembler.instance()

        if root_path:
            assembler.root_path = root_path
        if configs_by_name:
            assembler.extra_configs_by_name = configs_by_name

        assembler.build_all()
        
    @logger.catch
    def build_all(self) -> None:
        """Send commands to build all given instances."""
        # Set root path environ for various usage within project.
        os.environ["PUFT_ROOT_PATH"] = self.root_path

        self._build_logger()
        self._build_injection()
        self._build_views()
        self._build_mappers()
        self._build_emitters()
        self._build_shell_processors()
        self._build_cli_cmds()

        # Call postponed build from created App.
        try:
            self.puft.postbuild()
        except NotImplementedError:
            pass

    @logger.catch
    def _build_logger(self) -> None:
        """Call chain to build logger."""
        # Try to find logger config cell and build logger class from it.
        if self.config_cells:
            try:
                logger_config_cell = NamedCell.find_by_name(self.config_cells, "logger")
            except ValueError:
                # Logger config is not attached.
                logger_config = None
            else:
                # Parse config mapping from cell and append extra configs, if they are given.
                logger_config = ConfigCell.parse(
                    config_cell=logger_config_cell, 
                    root_path=self.root_path, 
                    update_with=self.extra_configs_by_name.get("logger", None)
                )
            self._init_logger_class(config=logger_config)

    @logger.catch
    def _init_logger_class(self, config: dict | None = None) -> None:
        """Build logger with given config.
        
        If config is None, build with default parameters."""
        # Use full or partially (with replacing missing keys from default) given config.
        logger_kwargs = self.DEFAULT_LOGGER_PARAMS
        if config:
            for k, v in config.items():
                logger_kwargs[k] = v
        logger.init_logger(**logger_kwargs)

    @logger.catch
    def _build_injection(self) -> None:
        self._run_builtin_injection_cells()
        self._run_custom_injection_cells()

    @logger.catch
    def _perform_database_postponed_setup(self) -> None:
        """Postponed setup is required, because Database uses Flask app to init native SQLAlchemy db inside, 
        so it's possible only after App initialization.
        The setup_db requires native flask app to work with."""
        self.database.setup(flask_app=self.puft.get_native_app())
    
    @logger.catch
    def _run_builtin_injection_cells(self) -> None:
        for cell in self.builtin_injection_cells:
            # Check for domain's config in given cells by comparing names and apply to service config if it exists.
            service_config = self._assemble_service_config(name=cell.name) 

            # Initialize service.
            if type(cell) is PuftInjectionCell:
                # Run special initialization with mode, host and port for Puft service.
                service = cell.service_class(
                    mode_enum=cell.mode_enum, host=cell.host, port=cell.port, 
                    config=service_config
                )
            else:
                service = cell.service_class(service_config=service_config)

            # Initialize controller.
            controller = cell.controller_class(service_class=cell.service_class)

            # Assign builtin cells to according Assembler vars to operate with later.
            if type(cell) is PuftInjectionCell:
                self.puft_controller = cell.controller_class.instance()
                self.puft = cell.service_class.instance()
            elif type(cell) is DatabaseInjectionCell:
                self.database_controller = cell.controller_class.instance()
                self.database = cell.service_class.instance()
                # Perform database postponed setup.
                self._perform_database_postponed_setup()

    @logger.catch
    def _run_custom_injection_cells(self) -> None:
        if self.injection_cells:
            for cell in self.injection_cells:
                # Check for domain's config in given cells by comparing names and apply to service config if it exists.
                service_config = self._assemble_service_config(name=cell.name) 

                # Initialize cell's service (first) and controller (second) singletons.
                cell.service_class(config=service_config)
                cell.controller_class(service_class=cell.service_class)

    @logger.catch
    def _assemble_service_config(self, name: str, is_errors_enabled: bool = False) -> dict:
        """Check for service's config in config cells by comparing its given name and return it as dict.

        If appropriate config hasn't been found, raise ValueError if `is_errors_enabled = True` or return empty dict otherwise."""
        if self.config_cells:
            config_cell_with_target_name = NamedCell.find_by_name(self.config_cells, name)
            if config_cell_with_target_name:
                config = ConfigCell.parse(
                    root_path=self.root_path, 
                    config_cell=config_cell_with_target_name,
                    update_with=self.extra_configs_by_name.get(name, None)
                )
                return config

        message = format_message("Appropriate config for given name {} hasn't been found.", name)
        if not is_errors_enabled:
            return {}
        else:
            raise ValueError(message)

    @logger.catch
    def _fetch_yaml_project_version(self) -> str:
        """Fetch project version from info.yaml from the root path and return it. 

        TODO: Replace this logic with senseful one. Better use configuration's version? Or __init__.py or main.py specified."""
        info_data = load_yaml(join_paths(self.root_path, "./info.yaml"))
        project_version = info_data["version"]
        return project_version

    @logger.catch
    def _build_views(self) -> None:
        """Build all views by registering them to app."""
        if self.view_cells:
            for view_cell in self.view_cells:
                self.puft.register_view(view_cell)

    @logger.catch
    def _build_mappers(self) -> None:
        """Assign models parameters to mapper classes."""
        if self.mapper_cells:
            for cell in self.mapper_cells:
                cell.mapper_class.set_orm_model(cell.model)

    @logger.catch
    def _build_emitters(self) -> None:
        """Build emitters from given cells and inject Puft application controllers to each."""
        if self.emitter_cells:
            for cell in self.emitter_cells:
                cell.emitter_class(puft_controller=self.puft_controller)

    @logger.catch
    def _build_shell_processors(self) -> None:
        if self.shell_processors:
            self.puft.register_shell_processor(*self.shell_processors)

    @logger.catch
    def _build_cli_cmds(self) -> None:
        if self.cli_cmds:
            self.puft.register_cli_cmd(*self.cli_cmds)
