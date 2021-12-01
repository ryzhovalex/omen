import os
import secrets
from typing import Any, List, Dict, Tuple, Callable, Union

from turbo_flask import Turbo
from warepy import logger, format_message, get_or_error
from flask import Flask, Blueprint, render_template, session, g
from flask_cors import CORS


from .domain import Domain
from ...helpers.cells import ViewCell
from ...helpers.constants import HTTP_METHODS, TurboAction


class Puft(Domain):
    """Puft class inherits Domain superclass.
    
    Implements Flask App operating layer."""
    @logger.catch
    def __init__(
        self, 
        config: dict,
        project_version: str = None,
        cli_cmds: List[Callable] = None,
        shell_processors: List[Callable] = None,
        is_ctx_processor_enabled: bool = False,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.project_version = project_version

        try:
            instance_path = config["INSTANCE_PATH"]
            template_folder = config["TEMPLATE_FOLDER"] 
            static_folder = config["STATIC_FOLDER"]
        except KeyError:
            error_message = format_message(
                "You must specify all of next parameters for app in config: INSTANCE_PATH, TEMPLATE_FOLDER, STATIC_FOLDER."
            )
            raise KeyError(error_message)

        self.app = Flask(
            __name__, 
            instance_path=instance_path, 
            template_folder=template_folder, 
            static_folder=static_folder
        )
        # Set server name for app from config.
        # try:
        #     self.app.config["SERVER_NAME"] = config["SERVER_NAME"]
        # except KeyError:
        #     error_message = format_message("You must specify key `SERVER_NAME` in your `app.json` config.")
        #     raise ValueError(error_message)

        # Enable CORS for the app's resources.
        is_cors_enabled = config.get("IS_CORS_ENABLED", None)
        if is_cors_enabled is not None:
            if is_cors_enabled:
                CORS(self.app)

        if config is not None:
            self.app.config.from_mapping(config)

        # Generate random hex token for App's secret key, if noone given in config.
        if self.app.config["SECRET_KEY"] is None:
            self.app.config["SECRET_KEY"] = secrets.token_hex(16)

        # Resolve context processor actions.
        self.is_ctx_processor_enabled = is_ctx_processor_enabled
        if self.is_ctx_processor_enabled:
            self.ctx_data = {}  # Live context data continiously pushed to app template context.

        # Initialize turbo.js.
        # src: https://blog.miguelgrinberg.com/post/dynamically-update-your-flask-web-pages-using-turbo-flask
        self.turbo = Turbo(self.app)
        if cli_cmds:
            self._register_cli_cmds(cli_cmds)
        if shell_processors:
            self._register_shell_processors(shell_processors)
        self._init_app_daemons()

    @logger.catch
    def get_app(self) -> Flask:
        """Return native app."""
        return self.app

    @logger.catch
    def get_version(self) -> str:
        """Return project's version."""
        return get_or_error(self.project_version)

    @logger.catch
    def get_instance_path(self) -> str:
        """Return app's instance path."""
        return self.app.instance_path

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

    @logger.catch
    def push_turbo(self, action: TurboAction, target: str, template_path: str, ctx_data: dict = {}) -> None:
        """Push turbo action to target with rendered from path template contextualized with given data.
        
        Args:
            action: Turbo-Flask action to perform.
            target: Id of HTML element to push action to.
            template_path: Path to template to render.
            ctx_data (optional): Context data to push to rendered template. Defaults to empty dict.
        """
        with self.app.app_context():
            action = action
            target = target
            template_path = template_path
            ctx_data = ctx_data
            exec(f"self.turbo.push(self.turbo.{action}(render_template('{template_path}', **{ctx_data}), '{target}'))")

    def postbuild(self) -> None:
        """Abstract method to perform post-injection operation related to app. Generally used by Assembler.
        
        Raise:
            NotImplementedError: If not re-implemented in children."""
        raise NotImplementedError("Method `postbuild` hasn't been reimplemented.")

    @logger.catch
    def _register_cli_cmds(self, cmds: List[Callable]) -> None:
        """Register cli cmds for the app."""
        for cmd in cmds:
            self.app.cli.add_command(cmd)

    @logger.catch
    def _register_shell_processors(self, shell_processors: List[Callable]) -> None:
        """Register shell processors for the app."""
        for processor in shell_processors:
            self.app.shell_context_processor(processor)

    @logger.catch
    def _init_app_daemons(self) -> None:
        """Binds various background processes to the app."""
        flask_app = self.get_app()

        if self.is_ctx_processor_enabled:
            @logger.catch
            @flask_app.context_processor
            def invoke_ctx_processor_operations():
                """Return continiously self live context data to app template processor.
                
                It might be useful in chain with turbo.js, when you push template changes
                and thus call flask context processor which in turn calls this return to template context."""
                return self.ctx_data

        @logger.catch
        @flask_app.before_request
        def invoke_each_request_operations():
            self._invoke_each_request_operations()

        @logger.catch
        @flask_app.before_first_request
        def invoke_first_request_operations():
            self._invoke_first_request_operations()

    def _invoke_each_request_operations(self) -> None:
        """Invoke before each request operations.
        
        Proxy function, can be extended in children with functions to call without changing `_init_app_daemons` function."""
        pass

    def _invoke_first_request_operations(self) -> None:
        """Invoke before first request operations.
        
        Proxy function, can be extended in children with functions to call without changing `_init_app_daemons` function."""
        pass
