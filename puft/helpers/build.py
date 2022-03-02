import os

from ..models.domains.cells import (
    ConfigCell, InjectionCell, MapperCell, ViewCell, EmitterCell
)

class Build:
    """Proxy mapping class with collection of initial project instances to be builded by assembler.
    
    Should be inherited by build class in root folder."""
    def __init__(
        self,
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

        self.config_cells = config_cells
        self.injection_cells = injection_cells
        self.mapper_cells = mapper_cells
        self.view_cells = view_cells
        self.emitter_cells = emitter_cells