import os
import pytest
from puft import Puft, Db, log, Error, NotFoundError, ModelNotFoundError
from warepy import load_yaml
from flask.testing import FlaskClient

from src.app.user.user import AdvancedUser, User
from src.app.badge.badge import Badge
from src.app.user.user_sv import UserSv


class TestUser():
    USERNAME = 'zerohero'
    PASSWORD = '1234'

    @pytest.fixture
    def user(self) -> User:
        user: User = User.create(
            username=self.USERNAME,
            password=self.PASSWORD)
        return user

    @pytest.fixture
    def push_user(self, app: Puft, db: Db, user: User) -> None:
        with app.app_context():
            db.add(user)
            db.commit()

    def test_get(
            self, app: Puft, push_user):
        with app.app_context():
            user = User.get_first(id=1)
        assert user.username == self.USERNAME
        assert user.check_password(self.PASSWORD)

    def test_del(
            self, app: Puft, push_user):
        with app.app_context():
            User.delete_first(id=1)

            try:
                User.get_first(id=1)
            except ModelNotFoundError:
                model_deleted = True
            else:
                model_deleted = False

            assert model_deleted, 'Model should have been properly deleted'


class TestAdvancedUser(TestUser):
    BADGE_NAME = 'Best User'

    @pytest.fixture
    def advanced_user(self, badge) -> AdvancedUser:
        user: AdvancedUser = AdvancedUser.create(
            username=self.USERNAME,
            password=self.PASSWORD,
            badge=badge)
        return user

    @pytest.fixture
    def badge(self, app: Puft) -> Badge:
        with app.app_context():
            return Badge.create(name=self.BADGE_NAME)

    @pytest.fixture
    def push_advanced_user(
            self, app: Puft, db: Db, advanced_user: AdvancedUser) -> None:
        with app.app_context():
            db.add(advanced_user)
            db.commit()

    def test_get_advanced_user_badge(
            self, app: Puft, push_advanced_user):
        with app.app_context():
            advanced_user = AdvancedUser.get_first(id=1)

            assert \
                type(advanced_user.badge_id) is int, \
                    'Advanced user should have integer badge_id'

            badge = Badge.get_first(id=advanced_user.badge_id)

            assert \
                badge.name == self.BADGE_NAME, \
                    'Badge of advanced user should have' \
                    f' name {self.BADGE_NAME}, got {badge.name} instead'
            assert advanced_user in badge.advanced_users


class TestUserApi(TestUser):
    def test_get(
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


class TestUserSv():
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
                'License number from config and license number from service' \
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
                'User service pc_hostname should equal config\'s pc_hostname'
