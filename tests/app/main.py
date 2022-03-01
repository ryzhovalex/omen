from puft import Build, InjectionCell, ViewCell

from dummy import DummyController, DummyService, DummyView


build = Build(
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
    