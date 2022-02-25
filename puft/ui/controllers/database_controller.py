from .controller import Controller
from ...models.services.database_service import DatabaseService


class DatabaseController(Controller):
    """Processes requests to Database Service."""
    def __init__(self, service_class: type[DatabaseService]) -> None:
        super().__init__(service_class)
        self.service = service_class.instance()