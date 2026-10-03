import functools
import inspect
import logging
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def log_arguments(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # Bind positional and keyword args to parameter names
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        # Log under the decorated function's module so messages are
        # attributed to the caller and honor its logger configuration.
        logger = logging.getLogger(func.__module__)
        args_str = "\n".join(
            f"  {param:<18}: {val}" for param, val in bound.arguments.items()
        )
        logger.debug(f"Executing {func.__name__} with arguments:\n{args_str}")

        return func(*args, **kwargs)
    return wrapper
