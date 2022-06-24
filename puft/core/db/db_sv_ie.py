from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass

from puft.core.sv.sv_ie import SvIe

if TYPE_CHECKING:
    from puft.core.db.db import Db


@dataclass
class DbSvIe(SvIe):
    """Injection cell with Db itself which can be applied to created
    application.
    """
    sv_class: type[Db]