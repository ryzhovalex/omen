from __future__ import annotations

from typing import TYPE_CHECKING

from .builder import Builder
from .assembler import Assembler

if TYPE_CHECKING:
    from flask.app import Flask


def create_app(*args, **kwargs) -> Flask:
    Assembler(build=Builder)
    return Assembler.create_app(*args, **kwargs)