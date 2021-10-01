from flask import Flask

from .controller import Controller


class OmenController(Controller):
    """Processes requests to Omen Service.

    Should be inherited by project's AppController."""
    def get_app(self) -> Flask:
        """Return native app."""
        return self.service.get_app()

    def get_version(self) -> str:
        """Return project's version."""
        return self.service.get_version()

    def replace_turbo(self, name: str, data: dict) -> None:
        """Update turbo element at given name with given data."""
        self.service.replace_turbo(name=name, data=data)