import json
from abc import abstractmethod
from typing import Any, List, Dict, Literal, Union, Callable

from warepy import logger, Singleton, format_message
from flask import Response, make_response, redirect, flash

from ..domains.domain import Domain


class Service(metaclass=Singleton):
    """Service superclass inherits Singleton metaclass.

    Layer between Domain Objects (Domains) and UI layer (Controllers and Views).
    Represents service with chained Domain 1:1. Performs various operations to prepare data (like json formatting) coming to Domains and from them."""
    def __init__(self, service_kwargs: Dict[str, Any], domain_class: Domain, domain_kwargs: Dict[str, Any]) -> None:
        self.params = service_kwargs
        # Create base model instance if it's given.
        if domain_class:
            self.domain = domain_class(**domain_kwargs)  # Create instance of given base model class with given kwargs

    def get_bound_by_id(self, id: int) -> Any:
        """Fetch bound instance by id from domain and return it."""
        return self.domain.get_bound_by_id(id=id)