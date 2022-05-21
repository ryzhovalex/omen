from puft import (
    Build, ServiceCell, ViewCell, ConfigCell, MapperCell, ErrorCell
)

from src.dummy import (
    Dummy, DummyError, DummyView, DummyMapper, ErrorView, dummy_processor, ctx_processor,
    each_request_processor, handle_dummy_error
)
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
            endpoint="dummy",
            view_class=DummyView,
            route="/"  
        ),
        ViewCell(
            endpoint="error",
            view_class=ErrorView,
            route="/error"  
        ),
    ],
    mapper_cells=[
        MapperCell(
            mapper_class=DummyMapper,
            model=User
        )
    ],
    error_cells=[
        ErrorCell(
            error_class=DummyError,
            handler_function=handle_dummy_error
        )
    ],
    shell_processors=[dummy_processor],
    ctx_processor_func=ctx_processor,
    each_request_func=each_request_processor
)
