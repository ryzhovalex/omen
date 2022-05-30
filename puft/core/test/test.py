import pytest
from puft import Puft, Db, get_root_path
from flask.testing import FlaskClient


class Test:
    @pytest.fixture
    def app(self):
        app: Puft = Puft.instance()
        yield app

    @pytest.fixture
    def db(self, app: Puft):
        db: Db = Db.instance()

        with app.app_context():
            db.drop_all()
            db.create_all()

        yield db

        with app.app_context():
            db.drop_all()

    @pytest.fixture()
    def client(self, app: Puft) -> FlaskClient:
        return app.test_client()

    @pytest.fixture()
    def root_path(self) -> str:
        return get_root_path()
