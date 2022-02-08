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
        config_cells_by_name: Dict[str, ConfigCell] = None,
        injection_cells_by_name: Dict[str, InjectionCell] = None, 
        mapper_cells_by_name: Dict[str, MapperCell] = None,
        view_cells_by_name: Dict[str, ViewCell] = None,
        emitter_cells_by_name: Dict[str, EmitterCell] = None
    ) -> None:
        # Use native root module path.
        # Because this class imported from root directory, root_path below will be assigned from there during class's initialization.
        # NOTE: This path can be overrided by assembler in order of getting arguments on it's own initialization.
        self.root_path = os.getcwd()

        self.app_injection_cell = app_injection_cell
        self.database_injection_cell = database_injection_cell
        self.config_cells_by_name = config_cells_by_name
        self.injection_cells_by_name = injection_cells_by_name
        self.mapper_cells_by_name = mapper_cells_by_name
        self.view_cells_by_name = view_cells_by_name
        self.emitter_cells_by_name = emitter_cells_by_name