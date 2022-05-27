import pytest
from puft import Puft, Db
from flask.testing import FlaskClient
from werkzeug.security import check_password_hash, generate_password_hash

from src.app.user.user import User


class TestUser():
    USERNAME = 'zerohero'
    PASSWORD = '1234'

    @pytest.fixture
    def user(self) -> User:
        user: User = User(
            username=self.USERNAME,
            password=generate_password_hash(self.PASSWORD))
        return user

    @pytest.fixture
    def push_user(self, app: Puft, db: Db, user: User) -> None:
        with app.app_context():
            db.push(user)

    def test_user_get(
            self, client: FlaskClient, push_user):
        data = client.get('/user/1').json
        if type(data) is dict:
            assert \
                'username' in data, \
                'User data should contain `username` field'
            assert \
                'password' not in data, \
                'User data shouldn\'t contain `password` field'
            assert \
                'post_ids' in data, \
                'User data should contain `post_ids` field'
            
            assert \
                data['username'] == self.USERNAME, \
                'Username should be as created one'
        else:
            raise TypeError(
                f'Unrecognized type of returned data: {type(data)}')
