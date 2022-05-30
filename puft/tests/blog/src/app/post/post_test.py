import pytest
from puft import Test
# from puft.tests.blog.src.app.user.user import User
from src.app.post.post import Post


class TestPost(Test):
    TITLE = 'Some post'
    DSCR = 'I love donuts!'
    USER_USERNAME = 'helloworld'
    USER_PASSWORD = '1234'

    # @pytest.fixture
    # def user(self) -> User:
    #     return User.create()

    # @pytest.fixture
    # def post(self, ) -> Post:
    #     return Post.create(
    #         title=self.TITLE,
    #         dscr=self.DSCR,
    #         user)
