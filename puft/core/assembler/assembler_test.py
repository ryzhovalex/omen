from pytest import fixture
from puft.core.assembler.assembler import Assembler
from puft.core.assembler.build import Build
from puft.core.cli.cli_run_enum import CLIRunEnum
from puft.core.app.puft import Puft
from puft.core.db.db import Db
from puft.tools.log import log
from puft.tests.integration.blog.app.user.user_sv import UserSv


@fixture
def assembler_dev(blog_build: Build, default_host: str, default_port: int):
    return Assembler(
        build=blog_build,
        mode_enum=CLIRunEnum.DEV,
        host=default_host,
        port=default_port)


class TestAssembler():
    def test_build(self, assembler_dev: Assembler):
        puft = Puft.instance()
        db = Db.instance()
        user_sv: UserSv = assembler_dev.custom_svs['UserSv']
