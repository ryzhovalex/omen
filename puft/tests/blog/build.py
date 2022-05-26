__version__ = "0.0.0"

from puft import (
    Build, ServiceCell, MapperCell, ViewCell
)


service_cells: list[ServiceCell] = [

]

mapper_cells: list[MapperCell] = [

]

view_cells: list[ViewCell] = [
]


build = Build(
    version=__version__,
    service_cells=service_cells,
    mapper_cells=mapper_cells,
    view_cells=view_cells)