import pytest
from puft import get_mode


@pytest.fixture
def special_id() -> int:
    return 3072


@pytest.fixture
def special_code(special_id) -> str:
    return f"Code: {special_id}"


@pytest.fixture
def app_mode() -> str:
    return get_mode()
