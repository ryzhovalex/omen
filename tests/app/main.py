from flask import Flask
from puft import Assembler, Build, InjectionCell

from dummy import DummyController, DummyService


build = Build(
    injection_cells=[
        InjectionCell(
            name="dummy",
            controller_class=DummyController,
            service_class=DummyService
        )
    ]
)


def create_app(*args, **kwargs) -> Flask:
    Assembler(build)
    return Assembler.create_app(*args, **kwargs)


if __name__ == "__main__":
    create_app().run()
    