import pytest
from src.app.user.user_test import TestUser
from src.app.user.user import AdvancedUser, User
from puft import Puft, Db, get_root_path
from flask.testing import FlaskClient

from src.app.badge.badge_test import badge, badge_mock
from src.app.user.user_test import user, advanced_user_with_badge, user_mock
# from src.app.post.post_test import 


# @pytest.fixture
# def app():
#     app: Puft = Puft.instance()
#     yield app


# @pytest.fixture()
# def client(app: Puft) -> FlaskClient:
#     return app.test_client()


# @pytest.fixture()
# def root_path() -> str:
#     return get_root_path()


# @pytest.fixture
# def db(app: Puft):
#     db: Db = Db.instance()

#     with app.app_context():
#         db.drop_all()
#         db.create_all()

#     yield db

#     with app.app_context():
#         db.drop_all()