from abc import ABCMeta, abstractmethod
from typing import Any, List, Dict, Tuple, Union, Literal, Callable, Type

from warepy import logger, Singleton

from ...models.services.service import Service


class Controller(Singleton):
    """Layer between Views and Services.
    
    Chained to Service singleton in 1:1 proportion."""
    def __init__(self, service_class: type[Service]) -> None:
        self.service = service_class.instance()
