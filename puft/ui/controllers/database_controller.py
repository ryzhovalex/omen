from .controller import Controller
from ...models.services.database import Database


class DatabaseController(Controller):
    """Processes requests to Database Service."""
    def __init__(self, service_class: type[Database]) -> None:
        super().__init__(service_class)
        self.service = service_class.instance()