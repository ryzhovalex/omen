from dataclasses import dataclass
import pytest
from puft import Puft, Mock
from src.app.badge.badge import Badge


@dataclass
class BadgeMock(Mock):
    name: str

@pytest.fixture
def badge_mock():
    return BadgeMock(name='BestUser')


@pytest.fixture
def badge(badge_mock: BadgeMock) -> Badge:
    return Badge.create(name=badge_mock.name)
