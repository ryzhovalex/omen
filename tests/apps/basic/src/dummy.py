import click

from puft import Service, Puft, View, Mapper, Database
from warepy import log
from flask.cli import with_appcontext

from .orm import User


def dummy_processor():
    return {
        "puft": Puft.instance(),
        "db": Database.instance(),
        "ctx": Puft.instance().get_native_app().test_request_context(),
        "User": User
    }


class Dummy(Service):
    def __init__(self, config: dict) -> None:
        super().__init__(config)

        self.app = Puft.instance()
        assert config.get("TEST_VAR", 0) == 12502


class DummyView(View):
    def get(self):
        db = Database.instance()
        db.create_all_tables()

        mapper = DummyMapper.instance()
        user = mapper.filter_first(id=1)
        return f"{user.username}: {user.firstname}"


class DummyMapper(Mapper):
    pass
