from flask import Flask

from .service import Service
from ..domains.puft import Puft
from ...constants.enums import TurboActionEnum


class PuftService(Service):
    """Operates over Puft processes.
    
    Should be inherited by project's AppService."""
    def __init__(self, service_kwargs: dict, domain_class: type[Puft], domain_kwargs: dict) -> None:
        super().__init__(service_kwargs, domain_class, domain_kwargs)
        self.domain = domain_class(**domain_kwargs)

    def get_app(self) -> Flask:
        """Return native app."""
        return self.domain.get_app()

    def get_version(self) -> str:
        """Return project's version."""
        return self.domain.get_version()

    def get_instance_path(self) -> str:
        """Return app's instance path."""
        return self.domain.get_instance_path()

    def push_turbo(self, action: TurboActionEnum, target: str, template_path: str, ctx_data: dict = {}) -> None:
        """Update turbo element at given name with given data."""
        self.domain.push_turbo(action=action, target=target, template_path=template_path, ctx_data=ctx_data)