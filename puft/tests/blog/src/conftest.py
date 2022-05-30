import pytest
from puft import Puft, Db, get_root_path
from flask.testing import FlaskClient


@pytest.fixture
def app():
    app: Puft = Puft.instance()

    yield app


@pytest.fixture
def db(app):
    db: Db = Db.instance()

    with app.app_context():
        db.drop_all()
        db.create_all()

    yield db

    with app.app_context():
        db.drop_all()


@pytest.fixture()
def client(app: Puft) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def root_path() -> str:
    return get_root_path()
