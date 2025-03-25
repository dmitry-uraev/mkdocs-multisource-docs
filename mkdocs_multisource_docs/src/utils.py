"""
Service functions
"""

import logging
import os
import shutil
import subprocess
import time
from argparse import ArgumentParser, Namespace
from functools import wraps
from pathlib import Path
from subprocess import CalledProcessError

from mkdocs_multisource_docs.src.constants import TMP_FOLDER_PATH

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


def setup_javadocs(path_to_java_project: Path):
    """
    New feature: jenerate javadoc for repository
    """
    logger.info('Building API documentation with Maven and Javadoc.')
    cwd = os.getcwd()
    os.chdir(path_to_java_project)

    try:
        call_args = [
            'mvn clean install javadoc:aggregate -Ddoclint=none -quiet',
        ]
        subprocess.run(' '.join(call_args), shell=True, check=True)
    except CalledProcessError:
        return None
    os.chdir(cwd)

    expected_path = path_to_java_project / 'target' / 'reports' / 'apidocs'
    if not expected_path.exists():
        raise FileNotFoundError

    logger.info('Successfully built API documentation.')
    destination_path = TMP_FOLDER_PATH / 'apidocs'
    shutil.move(src=expected_path, dst=destination_path)
    logger.info('API Documentation placed at %s', destination_path)

    return destination_path


def parse() -> Namespace:
    """
    Setup configuration parameters
    :return: ArgumentParser instance
    """
    parser = ArgumentParser(
        prog='Internal documentation builder tool',
        description='Gathers documentation from dev repos using Git and creates master index',
    )
    parser.add_argument(
        '--no-javadoc', type=bool, required=False, default=False,
        help='Full path to git project with docs'
    )
    return parser.parse_args()
