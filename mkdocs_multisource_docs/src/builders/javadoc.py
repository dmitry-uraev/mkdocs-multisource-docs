"""
Javadoc builder
"""

import logging
import os
import shutil
import subprocess
from pathlib import Path
from subprocess import CalledProcessError
from typing import Optional

from mkdocs_multisource_docs.src.config import AppConfig
from mkdocs_multisource_docs.src.constants import (BUILD_FOLDER_PATH,
                                                   JAVADOC_FOLDER_PATH)

logger = logging.getLogger(__name__)


def build_javadoc(
        path_to_java_project: Path,
        javadoc_command: Optional[str] = None,
        relative_directory: Optional[str] = None) -> None:
    """
    Generate javadoc for Java repository with customizable command and directory.

    Args:
        path_to_java_project: Root path to the Java project
        javadoc_command: Custom command for javadoc generation.
                        If None, uses default command (with mvn).
        relative_directory: Relative directory path within the project where
                          javadoc should be generated from. If None, uses
                          project root.
    """

    cwd = os.getcwd()

    # select working directory
    target_dir = path_to_java_project / relative_directory if relative_directory else path_to_java_project
    if not target_dir.exists():
            raise FileNotFoundError(f"Directory {target_dir} not found in project")
    os.chdir(target_dir)

    # build documentation
    try:
        call_args = [javadoc_command if javadoc_command else "mvn javadoc:aggregate -Ddoclint=none -quiet"]
        subprocess.run(' '.join(call_args), shell=True, check=True)
    except CalledProcessError as e:
        os.chdir(cwd)
        logger.error(f"Javadoc generation failed with error: {e}")
        return None
    except Exception as e:
        os.chdir(cwd)
        logger.error(f"Unexpected error during javadoc generation: {e}")
        return None

    os.chdir(cwd)

    # check javadoc generation
    expected_path = target_dir / 'target' / 'apidocs'
    if not expected_path.exists():
        raise FileNotFoundError(f"Javadoc not found at expected location: {expected_path}")

    logger.info('Successfully built and placed API documentation at %s.',
                Path('apidocs') / path_to_java_project.name)

    # move to destination
    destination_path = JAVADOC_FOLDER_PATH / f'{path_to_java_project.name}'
    shutil.move(src=expected_path, dst=destination_path)

def build_javadocs(app_conf: AppConfig) -> None:
    """
    Iterates over DocRepository objects in AppConfig
    Calls build_javadoc function for each appropriate repository
    """
    logger.info('Building API documentation...')
    for repo in app_conf.DOCS_REPOSITORIES:
        if repo.javadoc:
            build_javadoc(
                BUILD_FOLDER_PATH / repo.name,
                repo.javadoc_command if repo.javadoc_command else None,
                relative_directory=repo.javadoc_relative_dir if repo.javadoc_relative_dir else None)
