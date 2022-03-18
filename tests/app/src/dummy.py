import click

from puft import Controller, Service, Puft, View, Mapper, Database
from warepy import log
from flask.cli import with_appcontext

from .orm import User


def dummy_processor():
    return {
        "puft": Puft.instance(),
        "db": Database.instance(),
        "ctx": Puft.instance().get_native_app().test_request_context()
    }


@click.command("add_user")
@click.argument("firstname")
@click.argument("surname")
@with_appcontext
def dummy_cli(firstname, surname):
    log.info(f"Add user {firstname} {surname}.")
    db = Database.instance()
    user = User(firstname=firstname, surname=surname)
    db.add_to_session(user)
    db.commit_session()


class DummyController(Controller):
    pass


class DummyService(Service):
    def __init__(self, config: dict) -> None:
        super().__init__(config)

        self.app = Puft.instance()
        assert config.get("TEST_VAR", 0) == 12502


class DummyView(View):
    def get(self):
        db = Database.instance()
        db.create_all_tables()

        # user = User(firstname="Max", surname="Kudr", username="Americanec", password="1337")
        # db.add_to_session(user)
        # db.commit_session()

        mapper = DummyMapper.instance()
        massimo = mapper.filter_first(id=1)
        return f"{massimo.username}: {massimo.firstname} {massimo.surname}"


class DummyMapper(Mapper):
    pass
