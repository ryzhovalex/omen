import os
from dataclasses import dataclass

import pytest
from puft import Puft, Db, log, ModelNotFoundError, Test, Mock
from warepy import load_yaml
from flask.testing import FlaskClient

from src.app.user.user import AdvancedUser, User
from src.app.badge.badge import Badge
from src.app.user.user_sv import UserSv


@dataclass
class UserMock(Mock):
    username: str
    password: str


@pytest.fixture
def user_mock() -> UserMock:
    return UserMock(
        username='helloworld',
        password='1234')


@pytest.fixture
def user(user_mock: UserMock) -> User:
    user: User = User.create(
        username=user_mock.username,
        password=user_mock.password)
    return user


@pytest.fixture
def advanced_user_with_badge(
        badge: Badge, user_mock: UserMock) -> AdvancedUser:
    user: AdvancedUser = AdvancedUser.create(
        username=user_mock.username,
        password=user_mock.password,
        badge=badge)
    return user


class TestUser(Test):
    def test_get(
            self,
            app: Puft,
            db: Db,
            user: User,
            user_mock: UserMock):
        with app.app_context():
            db.push(user)
            new_user: User = User.get_first()

            assert new_user.username == user_mock.username
            assert new_user.check_password(user_mock.password)

    def test_del(
            self,
            app: Puft,
            db: Db,
            user: User):
        with app.app_context():
            db.push(user)
            User.delete_first()

            try:
                User.get_first()
            except ModelNotFoundError:
                model_deleted = True
            else:
                model_deleted = False

            assert model_deleted, 'Model should have been properly deleted'


class TestAdvancedUser(TestUser):
    def test_get_advanced_user_badge(
            self,
            app: Puft,
            db: Db,
            advanced_user_with_badge: AdvancedUser,
            badge: Badge):
        with app.app_context():
            db.push(advanced_user_with_badge)
            new_advanced_user: AdvancedUser = AdvancedUser.get_first()

            assert \
                type(new_advanced_user.badge_id) is int, \
                    'Advanced user should have integer badge_id'
            assert new_advanced_user in badge.advanced_users


class TestUserApi(TestUser):
    def test_get(
            self,
            app: Puft,
            db: Db,
            user: User,
            client: FlaskClient,
            user_mock: UserMock):
        with app.app_context():
            db.push(user) 

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
                data['username'] == user_mock.username, \
                    'Username should be as created one'
        else:
            raise TypeError(
                f'Unrecognized type of returned data: {type(data)}')


class TestUserSv(Test):
    @pytest.fixture
    def user_sv(self) -> UserSv:
        return UserSv.instance()

    @pytest.fixture
    def yaml_config(self, root_path) -> dict:
        return load_yaml(os.path.join(root_path, 'src/configs/user.yaml'))

    @pytest.fixture
    def yaml_user_system_token(self, yaml_config) -> str:
        try:
            return yaml_config['user_system_token']
        except KeyError:
            raise KeyError('Config should define `user_system_token`')

    @pytest.fixture
    def user_system_token_environ(self) -> str:
        try:
            return os.environ['BLOG_USER_SYSTEM_TOKEN']
        except KeyError:
            raise KeyError('OS should define environ BLOG_USER_SYSTEM_TOKEN')

    def test_license_number(self, user_sv: UserSv, yaml_config: dict):
        license_number: int = user_sv.get_license_number()
        yaml_license_number: int = yaml_config.get('license_number', '')

        assert \
            yaml_license_number != '', \
                'Config should define `license_number`'
        assert \
            license_number == yaml_license_number, \
                'License number from config and license number from sv' \
                ' should be the same'

    def test_pc_hostname(
            self,
            user_sv: UserSv,
            user_system_token_environ: str,
            yaml_user_system_token: str):
        user_system_token: str = user_sv.get_user_system_token()
        yaml_replaced_user_system_token: str = yaml_user_system_token.replace(
            '{HOSTNAME}', user_system_token_environ)

        assert \
            user_system_token == yaml_replaced_user_system_token, \
                'User sv pc_hostname should equal config\'s pc_hostname'
