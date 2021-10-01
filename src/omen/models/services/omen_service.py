from flask import Flask

from .service import Service


class OmenService(Service):
    """Operates over Omen processes.
    
    Should be inherited by project's AppService."""
    def get_app(self) -> Flask:
        """Return native app."""
        return self.domain.get_app()

    def get_version(self) -> str:
        """Return project's version."""
        return self.domain.get_version()

    def update_turbo(self, name: str, data: dict) -> None:
        """Update turbo element at given name with given data."""
        self.domain.update_turbo(name=name, data=data)