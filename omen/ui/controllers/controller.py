from abc import ABCMeta, abstractmethod
from typing import Any, List, Dict, Tuple, Union, Literal, Callable

from ...helpers.logger import logger
from ...helpers.singleton import Singleton
from ...models.services.service import Service


class Controller(metaclass=Singleton):
    """Layer between Views and Services."""
    def __init__(self, controller_kwargs: Dict[str, Any], service_class: Service) -> None:
        self.params = controller_kwargs
        # Just init service class without kwargs, because it's suppossed to be instantiated before with Domain object injected.
        self.service = service_class()

    @logger.catch
    def get_bound_by_id(self, id: int) -> Any:
        """Call method to get bound key instance to appropriate service by given id of the instance and return it's output."""
        return self.service.get_bound_by_id(id=id)