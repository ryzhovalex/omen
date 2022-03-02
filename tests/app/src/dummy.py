from puft import Controller, Service, Puft, View


class DummyController(Controller):
    pass


class DummyService(Service):
    def __init__(self, service_config: dict) -> None:
        super().__init__(service_config)

        self.app = Puft.instance()
        assert service_config.get("TEST_VAR", 0) == 12502

class DummyView(View):
    def get(self):
        return "hello, world!"