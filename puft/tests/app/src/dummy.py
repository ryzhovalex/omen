from puft import Service, Puft, View, Mapper, Database, get_mode, Error
from warepy import log, format_message
from flask import render_template, request

from src.orm import User, Message, Base, Admin


def ctx_processor():
    return {"safe_days": 665}


def each_request_processor():
    log.info(f"User connected {request.remote_addr}")


def handle_dummy_error(err):
    log.debug(err)
    return f"Dummy error: {err}"


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
        self.var = self.config.get("var")
        self.path_environ = self.config.get("path_environ")
        self.non_environ = self.config.get("non_environ")


class DummyView(View):
    def get(self):
        db = Database.instance()
        db.create_all_tables()

        mapper = DummyMapper.instance()
        user = mapper.filter_first(id=1)
        return render_template("dummy.html", user=user)


class ErrorView(View):
    def get(self):
        err_type = request.args.get("type", "error")
        if err_type == "dummy":
            raise DummyError("Hello dummy")
        else:
            raise Error(
                "Hello default error", 404)


class DummyMapper(Mapper):
    pass



class DummyError(Error):
    def expose(self):
        return "DummyError works!"
