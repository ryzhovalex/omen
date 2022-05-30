from dataclasses import dataclass

from puft.core.assembler.named_cell import NamedCell
from puft.core.service import Service


@dataclass
class ServiceCell(NamedCell):
    service_class: type[Service]
