import os
import sys
import inspect
from typing import Literal
from functools import wraps

from loguru import logger as loguru
from warepy import Singleton


class log(Singleton):
    """Logger tool responsible of writing all actions to logs.

    Simply said - it is a extra layer over `loguru.log` for keeping one log
    sink through all program.
    """
    native_log = loguru

    # Initialize class function variables.
    debug = native_log.debug
    info = native_log.info
    warning = native_log.warning
    error = native_log.error
    critical = native_log.critical

    @classmethod
    def catch(cls, func):
        """Log occured exceptions in function if it hasn't been done before and reraise it to higher level in any case."""
        @wraps(func)
        def inner(*args, **kwargs):
            # If error is logged, add extra message with it's module and function names.
            # Of course, better to put this data directly to code loguru context constructors, 
            # but it requires more deeper researching of loguru project itself, so it could be done later to improve this functionality.
            # But for now, enjoy parsing `extra` field of loguru's output :-).
            try:
                output = func(*args, **kwargs)
            except Exception as error:
                if len(error.args) == 2: # i.e some catcher already signed this error
                    # Just reraise error without logging.
                    raise error
                else:
                    inspect_module = inspect.getmodule(func)
                    if inspect_module:
                        node_info = inspect_module.__name__ + "." + func.__name__
                        with cls.native_log.contextualize(node=node_info):
                            # TODO: Calibrate concept of using proper loguru catch functionality on error.
                            # reraise=True required since loguru should properly logger error, but only where it
                            # originally raised (not in any other place in chain), and then reraise it to push it
                            # up through the chain to head_catch.
                            # @loguru.catch(reraise=True)
                            # def raiser():
                            #     # Log and reraise error with new sign node argument.
                            #     log.error(f"{error.__class__.__name__}: {error}")
                            #     raise error.__class__(node_info, error.args[0])
                            # raiser()
                            # Log and reraise error with new sign node argument.
                            log.error(f"{error.__class__.__name__}: {error}")
                            raise error.__class__(node_info, error.args[0])

            else:
                return output
        return inner

    @classmethod
    def _create(cls, *args, **kwargs) -> int:
        return cls.native_log.add(*args, **kwargs)

    @classmethod
    def _remove(cls, id: int) -> None:
        cls.native_log.remove(id)

    @classmethod
    def get_native_log(cls):
        return cls.native_log

    @classmethod
    def bind(cls, **kwargs):
        return cls.native_log.bind(**kwargs)

    @classmethod
    def configure(
        cls,
        *, 
        path: str, 
        format: str, 
        rotation: str, 
        level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        serialize: bool,
        delete_old: bool = False
    ) -> None:
        """Init log model instance depending on given arguments. 

        Just a helpful method to recognize which arguments should be added with
        type hinting, and which is remain static.
        
        Remove previous old log if `delete_old=True`.
        """
        if (
                delete_old
                and os.path.isfile(path)
                # Ensure that specified file is log for security
                and path.split('.')[-1] == 'log'):
            os.remove(path)

        cls._create(
            path, 
            format=format, 
            level=level,
            compression="zip", 
            rotation=rotation, 
            serialize=serialize
        )