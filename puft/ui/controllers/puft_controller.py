from flask import Flask

from .controller import Controller
from ...helpers.constants import TurboAction


class PuftController(Controller):
    """Processes requests to Puft Service.

    Should be inherited by project's AppController."""
    def get_app(self) -> Flask:
        """Return native app."""
        return self.service.get_app()

    def get_version(self) -> str:
        """Return project's version."""
        return self.service.get_version()

    def push_turbo(self, action: TurboAction, target: str, template_path: str, ctx_data: dict = {}) -> None:
        """Update turbo element at given name with given data."""
        self.service.push_turbo(action=action, target=target, template_path=template_path, ctx_data=ctx_data)