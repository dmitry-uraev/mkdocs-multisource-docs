"""
Javadoc builder
"""

import logging
import os
import shutil
import subprocess
from pathlib import Path
from subprocess import CalledProcessError

from mkdocs_multisource_docs.src.config import AppConfig
from mkdocs_multisource_docs.src.constants import (BUILD_FOLDER_PATH,
                                                   JAVADOC_FOLDER_PATH)

logger = logging.getLogger(__name__)


def build_javadoc(path_to_java_project: Path) -> None:
    """
    New feature: jenerate javadoc for repository
    """

    cwd = os.getcwd()
    os.chdir(path_to_java_project)

    try:
        call_args = [
            # 'mvn clean install javadoc:aggregate -Ddoclint=none -quiet',
            'mvn clean package -T 1C javadoc:aggregate -Ddoclint=none -quiet -DskipTests',
        ]
        subprocess.run(' '.join(call_args), shell=True, check=True)
    except CalledProcessError:
        return None
    os.chdir(cwd)

    expected_path = path_to_java_project / 'target' / 'reports' / 'apidocs'
    if not expected_path.exists():
        raise FileNotFoundError

    logger.info('Successfully built and placed API documentation at %s.',
                Path('apidocs') / path_to_java_project.name)
    destination_path = JAVADOC_FOLDER_PATH / f'{path_to_java_project.name}'
    shutil.move(src=expected_path, dst=destination_path)

def build_javadocs(app_conf: AppConfig) -> None:
    """
    Iterates over DocRepository objects in AppConfig
    Calls build_javadoc function for each appropriate repository
    """
    logger.info('Building API documentation with Maven and Javadoc.')
    for repo in app_conf.DOCS_REPOSITORIES:
        if repo.javadoc:
            build_javadoc(BUILD_FOLDER_PATH / repo.name)
