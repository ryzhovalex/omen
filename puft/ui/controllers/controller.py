from abc import ABCMeta, abstractmethod
from typing import Any, List, Dict, Tuple, Union, Literal, Callable, Type

from warepy import logger, Singleton

from ...models.services.service import Service


class Controller(metaclass=Singleton):
    """Layer between Views and Services."""
    def __init__(self, controller_kwargs: dict, service_class: Type[Service]) -> None:
        self.params = controller_kwargs

        # Just init service class without kwargs, because it's suppossed to be instantiated before with Domain object injected.
        self.service = service_class()  # type: ignore

    @logger.catch
    def get_bound_by_id(self, id: int) -> Any:
        """Call method to get bound key instance to appropriate service by given id of the instance and return it's output."""
        return self.service.get_bound_by_id(id=id)