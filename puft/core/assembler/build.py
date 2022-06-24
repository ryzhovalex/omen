import os
from typing import Callable
from puft.core.sock.default_sock_error_handler import default_sock_error_handler
from puft.core.sock.sock_ie import SockIe

from puft.core.sv.sv_ie import SvIe
from puft.core.view.view_ie import ViewIe
from puft.core.emt.emt_ie import EmtIe
from puft.core.error.error_ie import ErrorIe


class Build:
    """Proxy mapping class with collection of initial project instances to be
    builded by assembler.
    
    Should be inherited by build class in root folder.
    """
    def __init__(
        self,
        version: str = "",
        config_dir: str = "./src/configs",
        sv_ies: list[SvIe] = [],
        view_ies: list[ViewIe] = [],
        emt_ies: list[EmtIe] = [],
        error_ies: list[ErrorIe] = [],
        shell_processors: list[Callable] = [],
        cli_cmds: list[Callable] = [],
        sock_ies: list[SockIe] = [],
        default_sock_error_handler: Callable = default_sock_error_handler,
        ctx_processor_func: Callable | None = None,
        each_request_func: Callable | None = None,
        first_request_func: Callable | None = None,
    ) -> None:
        # Use native root module path.
        # Because this class imported from root directory, root_path below will be assigned from there during class's
        # initialization.
        # NOTE: This path can be overrided by assembler in order of getting arguments on it's own initialization.
        self.root_path = os.getcwd()

        self.version = version
        self.config_dir = config_dir
        self.sv_ies = sv_ies
        self.view_ies = view_ies
        self.emt_ies = emt_ies
        self.error_ies = error_ies
        self.shell_processors = shell_processors
        self.cli_cmds = cli_cmds
        self.ctx_processor_func = ctx_processor_func
        self.each_request_func = each_request_func
        self.first_request_func = first_request_func
        self.sock_ies = sock_ies
        self.default_sock_error_handler = default_sock_error_handler
