from puft import Build, ServiceCell, ViewCell, ConfigCell, MapperCell

from src.dummy import Dummy, DummyView, DummyMapper, dummy_processor
from src.orm import User


build = Build(
    service_cells=[
        ServiceCell(
            name="dummy",
            service_class=Dummy
        )
    ],
    view_cells=[
        ViewCell(
            name="dummy",
            view_class=DummyView,
            route="/"  
        )
    ],
    mapper_cells=[
        MapperCell(
            name="dummy",
            mapper_class=DummyMapper,
            model=User
        )
    ],
    shell_processors=[dummy_processor],
)
    
