from dataclasses import dataclass

from puft.core.ie.ie import Ie

from .view import View


@dataclass
class ViewIe(Ie):
    route: str  # Route will be the same for all methods.
    view_class: type[View]
    endpoint: str | None = None

    def get_transformed_route(self) -> str:
        """Return route transformed to endpoint format.

        This method used by app to get endpoint if it's not given at assembling
        stage.
        
        Example:
        ```python
        v = ViewIe(view_class=MyViewClass, route='/my/perfect/route')
        v.get_transformed_route()
        # 'my.perfect.route'
        ```
        """
        route_pieces: list[str] = self.route.split('/')
        return '.'.join(route_pieces)
