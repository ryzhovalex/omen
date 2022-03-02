from puft import Controller, Service, Puft, View


class DummyController(Controller):
    pass


class DummyService(Service):
    def __init__(self, config: dict) -> None:
        super().__init__(config)

        self.app = Puft.instance()
        assert config.get("TEST_VAR", 0) == 12502

class DummyView(View):
    def get(self):
        return "hello, world!"