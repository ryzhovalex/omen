from flask import Flask
from warepy import logger

from .service import Service
from ..domains.puft import Puft
from ...constants.enums import TurboActionEnum
from ...constants.hints import CLIModeEnumUnion


class PuftService(Service):
    """Operates over Puft processes.
    
    Should be inherited by project's AppService."""
    def __init__(
        self, service_config: dict,
        mode_enum: CLIModeEnumUnion,
        host: str,
        port: int
    ) -> None:
        super().__init__(service_config)
        self.mode_enum = mode_enum
        self.host = host
        self.port = port

        # Resolve Flask debug mode.
        if self.mode_enum.value in ("dev", "test"): 
            self.is_flask_in_debug = True
        else:
            self.is_flask_in_debug = False

        # Service config also Puft's domain config (especially it's Flask related part) so it can be pushed like so.
        self.puft = Puft(mode_enum=mode_enum, config=service_config)

    def get_native_app(self) -> Flask:
        """Return native app."""
        return self.puft.get_native_app()

    def get_instance_path(self) -> str:
        """Return app's instance path."""
        return self.puft.get_instance_path()

    @logger.catch
    def run(self) -> None:
        """Run Puft app using defined mode, host and port."""
        self.puft.run(host=self.host, port=self.port, is_debug=self.is_flask_in_debug)

    def push_turbo(self, action: TurboActionEnum, target: str, template_path: str, ctx_data: dict = {}) -> None:
        """Update turbo element at given name with given data."""
        self.puft.push_turbo(action=action, target=target, template_path=template_path, ctx_data=ctx_data)