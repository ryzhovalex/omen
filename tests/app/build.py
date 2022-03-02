from puft import Build, InjectionCell, ViewCell, ConfigCell

from src.dummy import DummyController, DummyService, DummyView


build = Build(
    config_cells=[
        ConfigCell(
            name="puft",
            source="./configs/puft.yaml"
        ),
        ConfigCell(
            name="dummy",
            source="./configs/dummy.yaml"
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
    ]
)
    