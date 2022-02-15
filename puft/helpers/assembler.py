from __future__ import annotations

import os
from typing import Dict, Any, List, Literal, Tuple, Callable, Union, TYPE_CHECKING, Type

from flask import Flask
from warepy import logger, join_paths, format_message, load_yaml

from .helper import Helper
from ..tools import find_cell_by_name, parse_config_cell
from .cells import AppInjectionCell, Cell, DatabaseInjectionCell, EmitterCell, MapperCell, InjectionCell, ViewCell, ConfigCell

if TYPE_CHECKING:
    from .build import Build
    from ..models.domains.puft import Puft
    from ..ui.controllers.puft_controller import PuftController


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
        build: Build,
        *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        # Define attributes for getter methods to be used at builder.
        self.extra_configs_by_name = {}  # Do not set this to None at initialization, because `get()` method called from this dictionary.
        self.root_path = build.root_path
        self.app_injection_cell = build.app_injection_cell
        self.database_injection_cell = build.database_injection_cell
        self.config_cells = build.config_cells
        self.injection_cells = build.injection_cells
        self.mapper_cells = build.mapper_cells
        self.view_cells = build.view_cells
        self.emitter_cells = build.emitter_cells

    @staticmethod
    @logger.catch
    def create_app(configs_by_name: Dict[str, dict] = None, root_path: str = None) -> Flask:
        """Initialize Flask app with assembler build context and return this app.
        
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

        assembler._build_all()
        flask_app = assembler.app.get_app()

        return flask_app
        
    @logger.catch
    def _build_all(self) -> None:
        """Send commands to build all given instances."""
        # Set root path environ for various usage within project.
        os.environ["PUFT_ROOT_PATH"] = self.root_path

        self._build_logger()
        self._build_injection()
        self._build_views()
        self._build_mappers()
        self._build_emitters()

        # Call postponed build from created App.
        try:
            self.app.postbuild()
        except NotImplementedError:
            pass

    @logger.catch
    def _build_logger(self) -> None:
        """Call chain to build logger."""
        # Try to find logger config cell and build logger class from it.
        if self.config_cells:
            logger_config_cell = find_cell_by_name(self.config_cells, "logger")
            if logger_config_cell is None:
                # Logger config is not attached.
                logger_config = None
            else:
                # Parse config mapping from cell and append extra configs, if they are given.
                logger_config = parse_config_cell(
                    config_cell=logger_config_cell, 
                    root_path=self.root_path, 
                    update_with=self.extra_configs_by_name.get("logger", None)
                )
            self._init_logger_class(config=logger_config)

    @logger.catch
    def _init_logger_class(self, config: dict = None) -> None:
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
        """Setup all injection instances: Controllers, Services and Domain Objects in 1:1:1 relation."""
        self._apply_project_version()
        self._run_injection_cells()

    @logger.catch
    def _perform_database_postponed_setup(self) -> None:
        """Postponed setup is required, because Database uses Flask app to init native SQLAlchemy db inside, 
        so it's possible only after App initialization.
        The setup_db requires native flask app to work with."""
        self.database.setup_db(flask_app=self.app.get_app())

    @logger.catch
    def _run_injection_cells(self) -> None:
        """Unpack injection cells with loop and init Service, by inject Domain, and Controller, by inject Service.
        
        Add config to cell's kwargs for domain, if one with the same name specified (e.g. you have config cell with name "app" and 
        injections cell with name "app" => domain "app" will receive configuration map from config cell."""
        # TODO: Refactor repeated initialization code for special and other cells.
        # Run special cells. #
        self._run_app_injection_cell()
        self._run_database_injection_cell()

        # Run other cells. #
        self._run_custom_injection_cells()
    
    @logger.catch
    def _run_app_injection_cell(self) -> None:
        # Look for config.
        # App config is required, so it's lack raises error, so give `is_errors_enabled` to enable errors raising on config problems.
        app_config = self._assemble_domain_kwargs_config(name="app", is_errors_enabled=True)
        if app_config:
            self.app_injection_cell.domain_kwargs["config"] = app_config

        # Initialize service and controller.
        self.app_injection_cell.service_class(
            service_kwargs=self.app_injection_cell.service_kwargs,
            domain_class=self.app_injection_cell.domain_class,
            domain_kwargs=self.app_injection_cell.domain_kwargs
        )
        self.app_controller = self.app_injection_cell.controller_class(
            controller_kwargs=self.app_injection_cell.controller_kwargs, 
            service_class=self.app_injection_cell.service_class
        )

        # Finally, assign app to use within assembler, since it was initialized at service initialization.
        self.app = self.app_injection_cell.domain_class.instance()

    @logger.catch
    def _run_database_injection_cell(self) -> None:
        if self.database_injection_cell:
            # Look for config.
            database_config = self._assemble_domain_kwargs_config(name="database")
            if database_config:
                self.database_injection_cell.domain_kwargs["config"] = database_config

            # Initialize service and controller.
            self.database_injection_cell.service_class(
                service_kwargs=self.database_injection_cell.service_kwargs,
                domain_class=self.database_injection_cell.domain_class,
                domain_kwargs=self.database_injection_cell.domain_kwargs
            )
            self.database_injection_cell.controller_class(
                controller_kwargs=self.database_injection_cell.controller_kwargs, 
                service_class=self.database_injection_cell.service_class
            )

            # Assign database domain if it exists to use within assembler.
            self.database = self.database_injection_cell.domain_class.instance()

            # Perform database postponed setup.
            self._perform_database_postponed_setup()

    @logger.catch
    def _run_custom_injection_cells(self) -> None:
        if self.injection_cells:
            for cell in self.injection_cells:
                domain_kwargs = cell.domain_kwargs
                # Check for domain's config in given cells by comparing names and apply to domain kwargs if it exists.
                config = self._assemble_domain_kwargs_config(name=cell.name) 
                if config:
                    domain_kwargs["config"] = config
                # Initialize cell's service (first) and controller (second) singletons.
                cell.service_class(service_kwargs=cell.service_kwargs, domain_class=cell.domain_class, domain_kwargs=domain_kwargs)
                cell.controller_class(controller_kwargs=cell.controller_kwargs, service_class=cell.service_class)

    @logger.catch
    def _assemble_domain_kwargs_config(self, name: str, is_errors_enabled: bool = False) -> dict:
        """Check for domain's config in config cells by comparing its given name and return it as dict.

        If appropriate config hasn't been found, write warning log (or raise ValueError if `is_errors_enabled = True`) and return empty dict."""
        if self.config_cells:
            config_cell_with_target_name = find_cell_by_name(self.config_cells, name)
            if config_cell_with_target_name:
                config = parse_config_cell(
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
    def _apply_project_version(self) -> None:
        """Try to fetch project version and apply it to app's domain kwargs."""
        # Try to fetch project version.
        project_version = None
        try:
            project_version = self._fetch_yaml_project_version()
        except FileNotFoundError:
            warn_message = format_message("The file `./info.yaml` is not specified under root path.")
            logger.warning(warn_message)
        except KeyError:
            warn_message = format_message("Project version is not specified in `./info.yaml` file.")
            logger.warning(warn_message)
        # Apply project version. It could be none, it is already handled within Puft domain.
        self.app_injection_cell.domain_kwargs["project_version"] = project_version

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
                self.app.register_view(view_cell)

    @logger.catch
    def _build_mappers(self) -> None:
        """Assign models parameters to mapper classes."""
        if self.mapper_cells:
            for cell in self.mapper_cells:
                cell.mapper_class.set_orm_model(cell.model)
                cell.mapper_class.set_params(cell.mapper_kwargs)

    @logger.catch
    def _build_emitters(self) -> None:
        """Build emitters from given cells and inject Puft application controllers to each."""
        if self.emitter_cells:
            for cell in self.emitter_cells:
                cell.emitter_class(app_controller=self.app_controller)