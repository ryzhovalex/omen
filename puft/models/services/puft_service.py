from flask import Flask

from .service import Service
from ...helpers.constants import TurboAction


class PuftService(Service):
    """Operates over Puft processes.
    
    Should be inherited by project's AppService."""
    def get_app(self) -> Flask:
        """Return native app."""
        return self.domain.get_app()

    def get_version(self) -> str:
        """Return project's version."""
        return self.domain.get_version()

    def push_turbo(self, action: TurboAction, target: str, template_path: str, ctx_data: dict = {}) -> None:
        """Update turbo element at given name with given data."""
        self.domain.push_turbo(action=action, target=target, template_path=template_path, ctx_data=ctx_data)