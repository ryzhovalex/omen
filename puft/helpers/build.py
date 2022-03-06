import os
from typing import Callable

from ..models.domains.cells import (
    ConfigCell, InjectionCell, MapperCell, ViewCell, EmitterCell
)

class Build:
    """Proxy mapping class with collection of initial project instances to be builded by assembler.
    
    Should be inherited by build class in root folder."""
    def __init__(
        self,
        version: str = "",
        config_cells: list[ConfigCell] = [],
        injection_cells: list[InjectionCell] = [], 
        mapper_cells: list[MapperCell] = [],
        view_cells: list[ViewCell] = [],
        emitter_cells: list[EmitterCell] = [],
        shell_processors: list[Callable] = [],
        cli_cmds: list[Callable] = []
        
    ) -> None:
        # Use native root module path.
        # Because this class imported from root directory, root_path below will be assigned from there during class's initialization.
        # NOTE: This path can be overrided by assembler in order of getting arguments on it's own initialization.
        self.root_path = os.getcwd()

        self.version = version
        self.config_cells = config_cells
        self.injection_cells = injection_cells
        self.mapper_cells = mapper_cells
        self.view_cells = view_cells
        self.emitter_cells = emitter_cells
        self.shell_processors = shell_processors
        self.cli_cmds = cli_cmds
