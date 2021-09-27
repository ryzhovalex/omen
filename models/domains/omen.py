import os
import secrets
from typing import Any, List, Dict, Tuple, Callable, Union

from turbo_flask import Turbo
from flask import Flask, Blueprint, render_template, session, g


from .domain import Domain
from ...helpers.logger import logger
from ...helpers.cells import TurboCell, ViewCell
from ...tools.stdkit import format_error_message
from ...helpers.constants import HTTP_METHODS


class Omen(Domain):
    """Omen class inherits Domain superclass.
    
    Implements Flask App operating layer.
    
    Args:
        config (optional): 
            Source to load app configuration from. It is a tuple with config load type and path to config ot dict, e.g.:
```
                config = ("json", "path/to/config.json")
```
            or, another example:
```
                config = ("map", {"ENV": "development", ...}
```
            Look for all load types in the typehint reference for class initialization.
    """
    def __init__(
        self, 
        config: dict = None,
        turbo_cells_by_name: Dict[str, TurboCell] = None,
        cli_cmds: List[Callable] = None,
        shell_processors: List[Callable] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        try:
            self.project_version = self.config["PROJECT_VERSION"]
        except KeyError:
            logger.warning("Project version hasn't been set in app config.")
            self.project_version = "not set"

        try:
            instance_path = config["INSTANCE_PATH"]
            template_folder = config["TEMPLATE_FOLDER"] 
            static_folder = config["STATIC_PATH"]
        except KeyError:
            error_message = format_error_message(
                "You must specify all of next parameters for app in config: INSTANCE_PATH, TEMPLATE_FOLDER, STATIC_PATH."
            )
            raise KeyError(error_message)

        self.app = Flask(
            __name__, 
            instance_path=instance_path, 
            template_folder=template_folder, 
            static_folder=static_folder
        )

        if config is not None:
            self.app.config.from_mapping(config)

        # Generate random hex token for App's secret key, if noone given in config.
        if self.app.config["SECRET_KEY"] is None:
            self.app.config["SECRET_KEY"] = secrets.token_hex(16)

        if turbo_cells_by_name:
            # Initialize turbo.js.
            # src: https://blog.miguelgrinberg.com/post/dynamically-update-your-flask-web-pages-using-turbo-flask
            self.turbo_cells_by_name = turbo_cells_by_name
            self.turbo = Turbo(self.app)
            self.is_turbo_enabled = True
        else:
            self.is_turbo_enabled = False

        if cli_cmds:
            self._register_cli_cmds(cli_cmds)
        if shell_processors:
            self._register_shell_processors(shell_processors)
        self._init_app_daemons()

    def get_app(self) -> Flask:
        """Return native app."""
        return self.app

    def get_version(self):
        """Return project's version."""
        return self.project_version

    @logger.catch
    def register_view(self, view_cell: ViewCell) -> None:
        """Register given view cell for the app."""
        # Check if view has kwargs to avoid sending empty dict.
        # Use cell's name as view's endpoint.
        if view_cell.view_kwargs:
            view = view_cell.view_class.as_view(view_cell.name, **view_cell.view_kwargs)
        else:
            view = view_cell.view_class.as_view(view_cell.name)
        self.app.add_url_rule(view_cell.route, view_func=view, methods=HTTP_METHODS)

    def _register_cli_cmds(self, cmds: List[Callable]) -> None:
        """Register cli cmds for the app."""
        for cmd in cmds:
            self.app.cli.add_command(cmd)

    def _register_shell_processors(self, shell_processors: List[Callable]) -> None:
        """Register shell processors for the app."""
        for processor in shell_processors:
            self.app.shell_context_processor(processor)

    def _init_app_daemons(self) -> None:
        """Binds various background processes to the app."""
        flask_app = self.get_app()

        @flask_app.context_processor
        def invoke_context_processor_operations():
            return self._invoke_context_processor_operations()

        @flask_app.before_request
        def invoke_each_request_operations():
            self._invoke_each_request_operations()

        @flask_app.before_first_request
        def invoke_first_request_operations():
            self._invoke_first_request_operations()

    def _invoke_ctx_processor_operations(self) -> Dict[str, Any]:
        """Invoke context processor operations and return dict of their results.

        Proxy function, can be extended in children with functions to call without changing `_init_app_daemons` function.

        Output of all operations should be written to `context_data` dictionary under appropriate key, e.g.:
        ```
            context_data["turbo"] = self.fetch_turbo() 
        ```
        """
        if self.is_turbo_enabled:
            ctx_data = {}
            # WARNING: Do not use key "turbo" for context data or you get conflict with existing key used by turbo.js.
            ctx_data["turbo_data"] = self.fetch_turbo()
            return ctx_data

    def _invoke_each_request_operations(self) -> None:
        """Invoke before each request operations.
        
        Proxy function, can be extended in children with functions to call without changing `_init_app_daemons` function."""
        pass

    def _invoke_first_request_operations(self) -> None:
        """Invoke before first request operations.
        
        Proxy function, can be extended in children with functions to call without changing `_init_app_daemons` function."""
        pass

    def fetch_turbo(self) -> None:
        """DUMMY!"""
        # data = self.get_turbo_data()
        # return data
        return 0

    @logger.catch
    def _push_turbo(self, target: str) -> None:
        """Push updates to turbo template."""
        with self.app.app_context():
            self.turbo.push(self.turbo.replace(render_template(f"operation/turbo-detection-message.html"), "turbo-detection-message"))