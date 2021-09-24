import os

from flask import Flask

from .assembler import Assembler


class Build:
    """Proxy mapping class with collection of initial instances to be builded by assembler.
    
    Should be copied manually/by script to project's root folder."""
    def __init__(self, assembler: Assembler) -> None:
        # Use native root module path.
        # NOTE: This path can be overrided by assembler.
        module_path = os.getcwd()

        # Basic cell instances that should be defined.
        config_cells_by_name = None
        injection_cells_by_name = None
        mapper_cells_by_name = None
        turbo_cells_by_name = None
        view_cells_by_name = None
        shell_processor_cells_by_name = None

    
def create_app(**kwargs) -> Flask:
    """Proxy reference to origin `create_app` method to be called from this root project directory by `flask run`."""
    return Assembler.create_app(build=Build, **kwargs)