from flask import Flask

from .service import Service
from ..domains.puft import Puft
from ...constants.enums import TurboActionEnum


class PuftService(Service):
    """Operates over Puft processes.
    
    Should be inherited by project's AppService."""
    def __init__(self, service_config: dict, domain_class: type[Puft], domain_kwargs: dict) -> None:
        super().__init__(service_config)
        # Service config also Puft's domain config (especially it's Flask related part) so it can be pushed like so.
        self.puft = Puft(config=service_config)

    def get_app(self) -> Flask:
        """Return native app."""
        return self.puft.get_app()

    def get_version(self) -> str:
        """Return project's version."""
        return self.puft.get_version()

    def get_instance_path(self) -> str:
        """Return app's instance path."""
        return self.puft.get_instance_path()

    def push_turbo(self, action: TurboActionEnum, target: str, template_path: str, ctx_data: dict = {}) -> None:
        """Update turbo element at given name with given data."""
        self.puft.push_turbo(action=action, target=target, template_path=template_path, ctx_data=ctx_data)