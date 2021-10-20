from ...models.domains.omen import Omen
from ...helpers.singleton import Singleton


class Emitter(metaclass=Singleton):
    """Emitter is a special class performing various tasks related to turbo.js actions, such as updating.
    
    It acts with Views, which calls methods from Emitters.
    
    Attributes:
        app: Omen application to work with, mainly using methods related to turbo.js."""
    def __init__(self, app: Omen) -> None:
        self.app = app