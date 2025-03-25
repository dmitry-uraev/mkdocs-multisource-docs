"""
Service functions
"""

import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def timeit(func):
    """Decorator that measures the execution time of a function.

    This decorator logs the execution time of the decorated function, including
    the function name and its arguments.

    Args:
        func (Callable): The function to be decorated.

    Returns:
        Callable: The wrapped function that logs execution time.
    """
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        logger.info('Function %s Took %s seconds with arguments %s%s %s',
                     func.__name__, f'{total_time:.4f}', func.__name__, args, kwargs)
        return result
    return timeit_wrapper
