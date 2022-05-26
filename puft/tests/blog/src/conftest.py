import pytest
from puft import Puft


@pytest.fixture
def app():
    app: Puft = Puft.instance()
    yield app


@pytest.fixture()
def client(app: Puft):
    return app.native_app.test_client()
