from warepy import logger, Singleton

from ..controllers.puft_controller import PuftController


class Emitter(Singleton):
    """Emitter is a special class performing various tasks related to turbo.js actions, such as updating.
    
    It acts with Views, which calls methods from Emitters.
    """
    def __init__(self, puft_controller: PuftController) -> None:
        self.puft_controller = puft_controller