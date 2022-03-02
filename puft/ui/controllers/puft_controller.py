from flask import Flask

from ...models.services.puft import Puft

from .controller import Controller
from ...constants.enums import TurboActionEnum


class PuftController(Controller):
    """Processes requests to Puft Service.

    Should be inherited by project's AppController."""
    def __init__(self, service_class: type[Puft]) -> None:
        super().__init__(service_class)
        self.service = service_class.instance()

    def get_native_app(self) -> Flask:
        """Return native app."""
        return self.service.get_native_app()

    def get_instance_path(self) -> str:
        """Return app's instance path."""
        return self.service.get_instance_path()

    def push_turbo(self, action: TurboActionEnum, target: str, template_path: str, ctx_data: dict = {}) -> None:
        """Update turbo element at given name with given data."""
        self.service.push_turbo(action=action, target=target, template_path=template_path, ctx_data=ctx_data)