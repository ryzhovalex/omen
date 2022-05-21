import os

import pytest
from dummy import Dummy
from warepy import format_message


@pytest.mark.parametrize("dummy_sv", [Dummy.instance()])
class TestDummy:
    def test_var(self, dummy_sv: Dummy, app_mode: str):
        assert dummy_sv.var is not None
        assert type(int(dummy_sv.var)) is int
        if app_mode == "prod":
            assert dummy_sv.var == 1
        elif app_mode == "dev":
            assert dummy_sv.var == 2
        elif app_mode == "test":
            assert dummy_sv.var == 3
        else:
            raise ValueError(
                format_message("Unrecognized app mode: {}", app_mode))
    
    def test_path_environ(self, dummy_sv: Dummy):
        assert dummy_sv.path_environ is not None
        assert type(dummy_sv.path_environ) is str
        assert os.environ["PATH"] in dummy_sv.path_environ 
    
    def test_non_environ(self, dummy_sv: Dummy):
        assert dummy_sv.non_environ is not None
        assert type(dummy_sv.non_environ) is str
        assert r"{configuration}" in dummy_sv.non_environ
    
    def test_fixtures(self, special_code):
        assert special_code == "Code: 3072"
