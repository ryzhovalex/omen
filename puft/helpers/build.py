import os
from typing import Any, List, Dict, Type

from .cells import AppInjectionCell, ConfigCell, DatabaseInjectionCell, InjectionCell, MapperCell, ViewCell, EmitterCell

class Build:
    """Proxy mapping class with collection of initial project instances to be builded by assembler.
    
    Should be inherited by build class in root folder."""
    def __init__(
        self,
        app_injection_cell: AppInjectionCell,
        database_injection_cell: DatabaseInjectionCell = None,
        config_cells: List[ConfigCell] = None,
        injection_cells: List[InjectionCell] = None, 
        mapper_cells: List[MapperCell] = None,
        view_cells: List[ViewCell] = None,
        emitter_cells: List[EmitterCell] = None
    ) -> None:
        # Use native root module path.
        # Because this class imported from root directory, root_path below will be assigned from there during class's initialization.
        # NOTE: This path can be overrided by assembler in order of getting arguments on it's own initialization.
        self.root_path = os.getcwd()

        self.app_injection_cell = app_injection_cell
        self.database_injection_cell = database_injection_cell
        self.config_cells = config_cells
        self.injection_cells = injection_cells
        self.mapper_cells = mapper_cells
        self.view_cells = view_cells
        self.emitter_cells = emitter_cells