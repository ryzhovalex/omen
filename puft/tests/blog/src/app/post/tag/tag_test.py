from dataclasses import dataclass

from pytest import fixture
from sqlalchemy.exc import IntegrityError
from puft import Puft, Db, Test, Mock, log

from src.app.post.tag.tag import Tag


@dataclass
class TagMock(Mock):
    name: str


@fixture
def tag_mock(tag_names: list[str]) -> TagMock:
    return TagMock(name=tag_names[0])


@fixture
def tag(tag_mock: TagMock) -> Tag:
    return Tag.create(name=tag_mock.name)


@fixture
def tags(tag_names: list[str]) -> list[Tag]:
    tags: list[Tag] = []

    for i in range(len(tag_names)):
        tags.append(Tag.create(name=tag_names[i]))

    return tags


@fixture
def tag_names() -> list[str]:
    return ['science', 'math', 'programming', 'fun']


class TestTag(Test):
    def test_get(self, app: Puft, db: Db, tag: Tag, tag_mock: TagMock):
        with app.app_context():
            db.push(tag)
            new_tag: Tag = Tag.get_first()

            assert \
                new_tag.name == tag_mock.name, \
                'Name of model and mock should be the same'

    def test_create_not_unique_name(
            self, app: Puft, db: Db, tag_names: list[str]):
        pass
        with app.app_context():
            db.push(Tag.create(name=tag_names[0]))

            try:
                db.push(Tag.create(name=tag_names[0]))
            except IntegrityError:
                pass
            else:
                raise AssertionError(
                    'Pushing another tag with the same name should raise'
                    ' sqlalchemy.exc.IntegrityError')
