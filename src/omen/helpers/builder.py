from __future__ import annotations
import os
from typing import TYPE_CHECKING, List, Dict, Any

from .logger import logger
from .constants import Path


class Builder:
    """Proxy mapping class with collection of initial project instances to be builded by assembler.
    
    Should be inherited by build class in root folder."""
    # Use native root module path.
    # NOTE: This path can be overrided by assembler.
    root_path = os.getcwd()

    # Basic cell instances that should be defined.
    config_cells_by_name = None
    injection_cells_by_name = None
    mapper_cells_by_name = None
    view_cells_by_name = None
    shell_processor_cells_by_name = None