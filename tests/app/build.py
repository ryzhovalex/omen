from puft import Build, InjectionCell, ViewCell, ConfigCell, MapperCell

from src.dummy import DummyController, DummyService, DummyView, DummyMapper, dummy_cli, dummy_processor
from src.orm import User


build = Build(
    config_cells=[
        ConfigCell(
            name="puft",
            source="./configs/puft.yaml"
        ),
        ConfigCell(
            name="dummy",
            source="./configs/dummy.yaml"
        ),
        ConfigCell(
            name="database",
            source="./configs/database.yaml"
        )
    ],
    injection_cells=[
        InjectionCell(
            name="dummy",
            controller_class=DummyController,
            service_class=DummyService
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
    