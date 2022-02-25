from .service import Service
from ..domains.database import Database


class DatabaseService(Service):
    """Operates over Database processes."""
    def __init__(self, service_config: dict) -> None:
        super().__init__(service_config)
        # For now service config propagated to Database domain.
        self.database = Database(config=service_config)