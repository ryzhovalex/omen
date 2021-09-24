import sys
import inspect
from functools import wraps
from typing import Callable, Literal, Type

from loguru import logger as loguru

from .helper import Helper
from .constants import Path


class logger(Helper):
    """Logger tool responsible of writing all actions to logs.

    Simply said - it is a extra layer over `loguru.logger` for keeping one logger through all program.

    Usage:
    ```
        from path.to.logger import logger
        logger(*your_args, **your_kwargs)
        logger.debug("hello!")
    ```
    """

    native_logger = loguru  # loguru.logger itself

    # Initialize class function variables.
    debug = native_logger.debug
    info = native_logger.info
    warning = native_logger.warning
    error = native_logger.error
    critical = native_logger.critical

    # Head catch decorator for final level of program with calling exit.
    head_catch = native_logger.catch(onerror=lambda _: sys.exit(1))

    # Original catch decorator for feeling free at args setting.
    origin_catch = native_logger.catch

    def __init__(self, *args, **kwargs) -> None:
        logger.create_logger(*args, **kwargs)

    @classmethod
    def catch(cls, func):
        """Log occured exceptions in function if it hasn't been done before and reraise it to higher level in any case."""
        @wraps(func)
        def inner(*args, **kwargs):
            # If error is logged, add extra message with it's module and function names.
            # Of course, better to put this data directly to code loguru context constructors, 
            # but it requires more deeper researching of loguru project itself, so it could be done later to improve this functionality.
            # But for now, enjoy parsing `extra` field of loguru's output :-).
            with cls.native_logger.contextualize(node=inspect.getmodule(func).__name__ + "." + func.__name__):
                try:
                    output = func(*args, **kwargs)
                except Exception as error:
                    if len(error.args) == 2: # i.e some catcher already signed this error
                        # Just reraise error without logging.
                        raise error
                    else:
                        # Log and reraise error with new sign argument.
                        logger.error(error)
                        raise error.__class__(error.args[0], True)
                else:
                    return output
        return inner

    @classmethod
    def create_logger(cls, *args, **kwargs) -> int:
        return cls.native_logger.add(*args, **kwargs)

    @classmethod
    def remove_logger(cls, id: int) -> None:
        cls.native_logger.remove(id)

    @classmethod
    def get_native_logger(cls):
        return cls.native_logger

    @staticmethod
    def init_logger(
        *, 
        logger_class: Callable, 
        path: Path, 
        format: str, 
        rotation: str, 
        level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        serialize: bool
    ) -> None:
        """Init logger model instance depending on given arguments. 

        Just a helpful method to recognize which arguments should be added with type hinting, and which is remain static."""
        logger_class(
            path, 
            format=format, 
            level=level,
            compression="zip", 
            rotation=rotation, 
            serialize=serialize
        ) 