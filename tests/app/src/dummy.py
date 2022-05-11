import os
from puft import Service, Puft, View, Mapper, Database, get_mode
from warepy import log, format_message
from flask import render_template, request

from .orm import User, Message, Base, Admin


def ctx_processor():
    return {"safe_days": 665}


def each_request_processor():
    log.info(f"User connected {request.remote_addr}")


def dummy_processor():
    return {
        "puft": Puft.instance(),
        "db": Database.instance(),
        "ctx": Puft.instance().get_native_app().test_request_context(),
        "User": User,
        "Message": Message,
        "Base": Base,
        "Admin": Admin
    }


class Dummy(Service):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.app = Puft.instance()

        log.debug(self.config)
        app_mode = get_mode()
        var = self.config.get("var")
        assert var is not None
        assert type(int(var)) is int
        if app_mode == "prod":
            assert var == 1
        elif app_mode == "dev":
            assert var == 2
        elif app_mode == "test":
            assert var == 3
        else:
            raise ValueError(
                format_message("Unrecognized app mode: {}", app_mode))
        path_environ = self.config.get("path_environ")
        assert path_environ is not None
        assert type(path_environ) is str
        assert \
            os.environ["PATH"] in path_environ 
        non_environ = self.config.get("non_environ")
        assert non_environ is not None
        assert type(non_environ) is str
        assert r"{configuration}" in non_environ


class DummyView(View):
    def get(self):
        db = Database.instance()
        db.create_all_tables()

        mapper = DummyMapper.instance()
        user = mapper.filter_first(id=1)
        return render_template("dummy.html", user=user)


class DummyMapper(Mapper):
    pass
