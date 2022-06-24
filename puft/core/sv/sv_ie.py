from dataclasses import dataclass

from puft.core.ie.named_ie import NamedIe
from puft.core.sv.sv import Sv


@dataclass
class SvIe(NamedIe):
    sv_class: type[Sv]
