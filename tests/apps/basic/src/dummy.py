from puft import Service, Puft, View, Mapper, Database
from warepy import log
from flask import render_template, request

from .orm import User


def ctx_processor():
    return {"safe_days": 665}


def each_request_processor():
    log.info(f"User connected {request.remote_addr}")


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
        assert config.get("test_var", 0) == 12502


class DummyView(View):
    def get(self):
        db = Database.instance()
        db.create_all_tables()

        mapper = DummyMapper.instance()
        user = mapper.filter_first(id=1)
        return render_template("dummy.html", user=user)


class DummyMapper(Mapper):
    pass
