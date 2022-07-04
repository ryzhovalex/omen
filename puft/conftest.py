import os
import sys

from pytest import fixture
from puft import (
    Build, SvIe, ViewIe, SockIe)

from puft.tests.integration.build import build as _blog_build
from puft.tools.log import log


@fixture
def blog_build() -> Build:
    build = _blog_build
    build.config_dir = './puft/tests/integration/blog/configs'

    return build


@fixture
def default_host() -> str:
    return '127.0.0.1'


@fixture
def default_port() -> int:
    return 6000
