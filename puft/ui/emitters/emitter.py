from ...constants.enums import TurboActionEnum
from warepy import logger, Singleton

from ..controllers.puft_controller import PuftController


class Emitter(Singleton):
    """Emitter is a special class performing various tasks related to turbo.js actions, such as updating.
    
    It acts with Views, which calls methods from Emitters.
    """
    def __init__(self, puft_controller: PuftController) -> None:
        self.puft_controller = puft_controller

    def push(
        self, action: TurboActionEnum, target: str, template_path: str, ctx_data: dict = {}  
    ) -> None:
        """Push turbo action to target with rendered from path template contextualized with given data.
        
        Args:
            action: Turbo-Flask action to perform.
            target: Id of HTML element to push action to.
            template_path: Path to template to render.
            ctx_data (optional): Context data to push to rendered template. Defaults to empty dict.
        """
        self.puft_controller.push_turbo(
            action=action,
            target=target,
            template_path=template_path,
            ctx_data=ctx_data
        )