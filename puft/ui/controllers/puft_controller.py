from flask import Flask

from ...models.services.puft_service import PuftService

from .controller import Controller
from ...constants.enums import TurboActionEnum


class PuftController(Controller):
    """Processes requests to Puft Service.

    Should be inherited by project's AppController."""
    def __init__(self, controller_kwargs: dict, service_class: type[PuftService]) -> None:
        super().__init__(controller_kwargs, service_class)
        self.service = service_class.instance()

    def get_app(self) -> Flask:
        """Return native app."""
        return self.service.get_app()

    def get_version(self) -> str:
        """Return project's version."""
        return self.service.get_version()

    def get_instance_path(self) -> str:
        """Return app's instance path."""
        return self.service.get_instance_path()

    def push_turbo(self, action: TurboActionEnum, target: str, template_path: str, ctx_data: dict = {}) -> None:
        """Update turbo element at given name with given data."""
        self.service.push_turbo(action=action, target=target, template_path=template_path, ctx_data=ctx_data)