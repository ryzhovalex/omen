from dataclasses import dataclass

import pytest
from puft import Test, Puft, Db, Mock

from src.app.post.post import Post
from src.app.user.user import User
from src.app.post.tag.tag import Tag


@dataclass
class PostMock(Mock):
    title: str
    content: str


@pytest.fixture
def post_mock() -> PostMock:
    return PostMock(title='Some post', content='I love donuts!')


@pytest.fixture
def post(user: User, post_mock: PostMock) -> Post:
    return Post.create(
        title=post_mock.title,
        content=post_mock.content,
        user=user)


@pytest.fixture
def post_with_tags(user: User, post_mock: PostMock, tags: list[Tag]) -> Post:
    return Post.create(
        title=post_mock.title,
        content=post_mock.content,
        user=user,
        tags=tags)


class TestPost(Test):
    def test_get(self, app: Puft, db: Db, post: Post, post_mock: PostMock):
        with app.app_context():
            db.push(post)
            new_post: Post = Post.get_first()
            new_user: User = User.get_first()

            assert \
                new_post.title == post_mock.title, \
                    'Post title should be the same as at mock'
            assert \
                new_post.content == post_mock.content, \
                    'Post content should be the same as at mock'

            assert \
                new_post.user_id == new_user.id, \
                    'Post should be connected with newly created user'

    def test_tags(
            self, app: Puft, db: Db, post_with_tags: Post, tags: list[Tag]):
        with app.app_context():
            db.push(post_with_tags)
            post: Post = Post.get_first()

            for tag in tags:
                assert tag in post.tags, 'Post should contain all tags'
