import pytest
from puft import Puft, Db
from flask.testing import FlaskClient


@pytest.fixture
def app():
    app: Puft = Puft.instance()

    yield app


@pytest.fixture
def db(app):
    db: Db = Db.instance()

    with app.app_context():
        db.create_all_tables()

    yield db

    with app.app_context():
        db.drop_all_tables()


@pytest.fixture()
def client(app: Puft) -> FlaskClient:
    return app.native_app.test_client()
