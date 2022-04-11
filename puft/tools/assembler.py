from __future__ import annotations

import os
from typing import Dict, TYPE_CHECKING, Any

from puft.constants.hints import CLIModeEnumUnion
from warepy import log, join_paths, format_message, load_yaml

from .helper import Helper
from ..models.domains.cells import (
    NamedCell, ConfigCell, ServiceCell, PuftServiceCell, DatabaseServiceCell
)
from ..models.services.database import Database
from ..models.services.puft import Puft
from ..constants.hints import CLIModeEnumUnion

if TYPE_CHECKING:
    from .build import Build


def get_mode() -> str:
    """Return app mode string representation."""
    return Assembler.instance().get_mode_enum().value
    

def get_root_path() -> str:
    """Return app project root path."""
    return Assembler.instance().get_root_path()


class Assembler(Helper):
    """Assembles all project instances from given `Builder` type's class and initializes it.
    
    Acts automatically and shouldn't be inherited directly by project in any form."""
    DEFAULT_LOG_PARAMS = {
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
        self.service_cells = build.service_cells
        self.mapper_cells = build.mapper_cells
        self.view_cells = build.view_cells
        self.emitter_cells = build.emitter_cells
        self.mode_enum = mode_enum
        self.shell_processors = build.shell_processors
        self.cli_cmds = build.cli_cmds

        self._assign_config_cells(build.config_dir)

        # Traverse given configs and assign enabled builtin cells.
        self._assign_builtin_service_cells(mode_enum, host, port)

    @log.catch
    def get_puft(self) -> Puft:
        return self.puft

    @log.catch
    def get_database(self) -> Database:
        return self.database

    @log.catch
    def get_root_path(self) -> str:
        return self.root_path

    @log.catch
    def get_mode_enum(self) -> CLIModeEnumUnion:
        return self.mode_enum

    @log.catch
    def _assign_config_cells(self, config_dir: str) -> None:
        """Traverse through config files under given config_dir and create ConfigCells from them.

        Name taken from filename of config and should be the same as specified at config's target service_cell.name.
        """
        self.config_cells = []

        config_path = join_paths(self.root_path, config_dir)
        for filename in os.listdir(config_path):
            # Pick only files under config_dir.
            if os.path.isfile(join_paths(config_path, filename)):
                name = filename[:filename.rfind(".")]  # Truncate extension.
                file_path = join_paths(config_path, filename)
                self.config_cells.append(ConfigCell(name=name, source=file_path))

    @log.catch
    def _assign_builtin_service_cells(self, mode_enum: CLIModeEnumUnion, host: str, port: int) -> None:
        """Assign builting service cells if configuration file for its service exists."""
        self.builtin_service_cells = [PuftServiceCell(
            name="puft",
            service_class=Puft,
            mode_enum=mode_enum,
            host=host,
            port=port
        )]  # type: list[Any]

        # Enable only modules with specified configs.
        if self.config_cells:
            try:
                NamedCell.find_by_name("database", self.config_cells)
            except ValueError:
                pass
            else:
                self.builtin_service_cells.append(DatabaseServiceCell(
                    name="database",
                    service_class=Database
                ))
                log.info("Database layer enabled.")

    @staticmethod
    @log.catch
    def build(
        configs_by_name: Dict[str, dict] | None = None, root_path: str | None = None
    ) -> None:
        """Initialize all given to Assembler instances in their dependencies.
        
        Reassign assembler's attributes to given ones and run it's setup operations to assemble app and other project's instances.

        Args:
            configs_by_name (optional):
                Configs to be appended to appropriate ones described in Build class. Defaults to None.
                Contain config name as key (which is compared to ConfigCell name field) and configuration mapping as value, e.g.:
        ```python
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
        
    @log.catch
    def build_all(self) -> None:
        """Send commands to build all given instances."""
        self._build_log()
        self._build_service()
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

    @log.catch
    def _build_log(self) -> None:
        """Call chain to build log."""
        # Try to find log config cell and build log class from it.
        if self.config_cells:
            try:
                log_config_cell = NamedCell.find_by_name("log", self.config_cells)
            except ValueError:
                # log config is not attached.
                log_config = None
            else:
                # Parse config mapping from cell and append extra configs, if they are given.
                log_config = log_config_cell.parse(
                    root_path=self.root_path, 
                    update_with=self.extra_configs_by_name.get("log", None)
                )
            self._init_log_class(config=log_config)

    @log.catch
    def _init_log_class(self, config: dict | None = None) -> None:
        """Build log with given config.
        
        If config is None, build with default parameters."""
        # Use full or partially (with replacing missing keys from default) given config.
        log_kwargs = self.DEFAULT_LOG_PARAMS
        if config:
            for k, v in config.items():
                log_kwargs[k] = v
        log.configure(**log_kwargs)

    @log.catch
    def _build_service(self) -> None:
        self._run_builtin_service_cells()
        self._run_custom_service_cells()

    @log.catch
    def _perform_database_postponed_setup(self) -> None:
        """Postponed setup is required, because Database uses Flask app to init native SQLAlchemy db inside, 
        so it's possible only after App initialization.
        The setup_db requires native flask app to work with."""
        self.database.setup(flask_app=self.puft.get_native_app())
    
    @log.catch
    def _run_builtin_service_cells(self) -> None:
        for cell in self.builtin_service_cells:
            # Check for domain's config in given cells by comparing names and apply to service config if it exists.
            config = self._assemble_service_config(name=cell.name) 

            # Initialize service.
            if type(cell) is PuftServiceCell:
                # Run special initialization with mode, host and port for Puft service.
                cell.service_class(
                    mode_enum=cell.mode_enum, host=cell.host, port=cell.port, 
                    config=config
                )
            else:
                cell.service_class(config=config)

            # Assign builtin cells to according Assembler vars to operate with later.
            if type(cell) is PuftServiceCell:
                self.puft = cell.service_class.instance()
            elif type(cell) is DatabaseServiceCell:
                self.database = cell.service_class.instance()
                # Perform database postponed setup.
                self._perform_database_postponed_setup()

    @log.catch
    def _run_custom_service_cells(self) -> None:
        if self.service_cells:
            for cell in self.service_cells:
                if self.config_cells:
                    # Check for domain's config in given cells by comparing names and apply to service config if it 
                    # exists.
                    service_config = self._assemble_service_config(name=cell.name) 
                else:
                    service_config = {}

                # Initialize cell's service (first) and controller (second) singletons.
                cell.service_class(config=service_config)

    @log.catch
    def _assemble_service_config(self, name: str, is_errors_enabled: bool = False) -> dict:
        """Check for service's config in config cells by comparing its given name and return it as dict.

        If appropriate config hasn't been found, raise ValueError if `is_errors_enabled = True` or return empty dict
        otherwise.
        """
        try:
            config_cell_with_target_name = NamedCell.find_by_name(name, self.config_cells)
        except ValueError:  # i.e config not found.
            # If config not found and errors enabled, raise error.
            if is_errors_enabled:
                message = format_message("Appropriate config for given name {} hasn't been found.", name)
                raise ValueError(message)
            else:
                config = {}
        else:
            config = config_cell_with_target_name.parse(
                root_path=self.root_path, 
                update_with=self.extra_configs_by_name.get(name, None)
            )

        return config

    @log.catch
    def _fetch_yaml_project_version(self) -> str:
        """Fetch project version from info.yaml from the root path and return it. 

        TODO: Replace this logic with senseful one. Better use configuration's version? Or __init__.py or main.py specified."""
        info_data = load_yaml(join_paths(self.root_path, "./info.yaml"))
        project_version = info_data["version"]
        return project_version

    @log.catch
    def _build_views(self) -> None:
        """Build all views by registering them to app."""
        if self.view_cells:
            for view_cell in self.view_cells:
                self.puft.register_view(view_cell)

    @log.catch
    def _build_mappers(self) -> None:
        """Assign models parameters to mapper classes."""
        if self.mapper_cells:
            for cell in self.mapper_cells:
                cell.mapper_class.set_orm_model(cell.model)

    @log.catch
    def _build_emitters(self) -> None:
        """Build emitters from given cells and inject Puft application controllers to each."""
        if self.emitter_cells:
            for cell in self.emitter_cells:
                cell.emitter_class(puft=self.puft)

    @log.catch
    def _build_shell_processors(self) -> None:
        if self.shell_processors:
            self.puft.register_shell_processor(*self.shell_processors)

    @log.catch
    def _build_cli_cmds(self) -> None:
        if self.cli_cmds:
            self.puft.register_cli_cmd(*self.cli_cmds)
