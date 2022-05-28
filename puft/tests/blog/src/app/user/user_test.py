import pytest
from puft import Puft, Db, log
from flask.testing import FlaskClient
from werkzeug.security import check_password_hash, generate_password_hash

from src.app.user.user import AdvancedUser, User
from src.app.badge.badge import Badge


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
            db.add(user)
            db.commit()

    def test_get(
            self, app: Puft, push_user):
        with app.app_context():
            user = User.get_first(id=1)
        assert user.username == self.USERNAME
        assert check_password_hash(user.password, self.PASSWORD)


class TestAdvancedUser(TestUser):
    BADGE_NAME = 'Best User'

    @pytest.fixture
    def advanced_user(self) -> AdvancedUser:
        user: AdvancedUser = AdvancedUser(
            username=self.USERNAME,
            password=generate_password_hash(self.PASSWORD))
        return user

    @pytest.fixture
    def push_advanced_user(
            self, app: Puft, db: Db, advanced_user: AdvancedUser) -> None:
        with app.app_context():
            db.add(advanced_user)
            db.commit()

    @pytest.fixture
    def badge(self, app: Puft) -> Badge:
        with app.app_context():
            return Badge(name=self.BADGE_NAME)

    @pytest.fixture
    def add_advanced_user_badge(
            self, app: Puft, db: Db, push_advanced_user, badge: Badge) -> None:
        with app.app_context():
            user: AdvancedUser = AdvancedUser.get_first(id=1)
            badge.advanced_users.append(user)
            db.commit()

    def test_get_advanced_user_badge(
            self, app: Puft, add_advanced_user_badge):
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
