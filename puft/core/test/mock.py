from dataclasses import dataclass

from puft.core.ie.ie import Ie


@dataclass
class Mock(Ie):
    """Interface using for mocking test data."""
    pass
