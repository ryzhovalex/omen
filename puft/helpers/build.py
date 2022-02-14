import os

from .cells import AppInjectionCell, ConfigCell, DatabaseInjectionCell, InjectionCell, MapperCell, ViewCell, EmitterCell

class Build:
    """Proxy mapping class with collection of initial project instances to be builded by assembler.
    
    Should be inherited by build class in root folder."""
    def __init__(
        self,
        app_injection_cell: AppInjectionCell,
        database_injection_cell: DatabaseInjectionCell = None,
        config_cells: list[ConfigCell] = None,
        injection_cells: list[InjectionCell] = None, 
        mapper_cells: list[MapperCell] = None,
        view_cells: list[ViewCell] = None,
        emitter_cells: list[EmitterCell] = None
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