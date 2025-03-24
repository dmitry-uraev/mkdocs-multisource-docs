"""
Functionality to process documentation archives
"""

import logging
import re
import shutil
import zipfile
from pathlib import Path

from mkdocs_multisource_docs.src.config import (AppConfig, DocRepository,
                                                get_application_config)
from mkdocs_multisource_docs.src.constants import (BUILD_FOLDER_PATH,
                                                   TMP_FOLDER_PATH)

logger = logging.getLogger(__name__)


class CorpusManager:
    """
    Process repositories archived documentation

    Uses TMP_FOLDER_PATH to store archives collected from git repositories.
    Unarchives all documents into BUILD_FOLDER_PATH.
    Removes TMP_FOLDER_PATH after processing all archives.
    """

    def __init__(self, artifacts_path: Path, application_config: AppConfig) -> None:

        logger.info('Initializing CorpusManager for directory %s}', TMP_FOLDER_PATH)
        self._corpus = artifacts_path
        self._config = application_config

        self._doc_map = {doc.name: doc for doc in self._config.DOCS_REPOSITORIES}

    def extract_documentation_from_artifacts(self) -> None:
        """
        We iterate over downloaded unarchived folders and check their content
        :return: None
        """
        logger.info(msg=f'Extracting repository archives in {TMP_FOLDER_PATH}')
        repo_names = extract_archives_in_folder(folder_path=self._corpus)

        for file in self._corpus.iterdir():
            if file.is_dir():
                for repo_name in repo_names:
                    if file.name.startswith(repo_name):
                        self._move_doc_directory(file=file, doc=self._doc_map[repo_name])

        logger.info(msg=f'Moved documentation found into {BUILD_FOLDER_PATH} folder')
        logger.info(msg=f'Deleting temporary folder {TMP_FOLDER_PATH}')
        shutil.rmtree(self._corpus)

    @staticmethod
    def _move_doc_directory(file: Path, doc: DocRepository):
        logger.info('Found documentation for repository: %s', doc.name)
        shutil.move(src=file, dst=BUILD_FOLDER_PATH / doc.name)


def extract_archive(archive_path: Path, destination_path: Path) -> None:
    """
    Extract zip archive
    :param archive_path: path to tgz archive
    :param destination_path: destination path to extract archive
    :return: None
    """
    with zipfile.ZipFile(file=archive_path, mode='r') as archive:
        archive.extractall(path=destination_path)


def extract_archives_in_folder(folder_path: Path) -> list:
    """
    Extract all zip archives in the folder specified
    :param folder_path: path to the folder, should be Path object
    :return: list of repository names extracted
    """
    pattern = r'export_(.*)\.zip'
    repo_names = []
    for file in folder_path.iterdir():
        if str(file).endswith('.zip'):
            logger.info(msg=f'Extracting archive from {TMP_FOLDER_PATH/file}')
            extract_archive(archive_path=file, destination_path=TMP_FOLDER_PATH)
            repo_names.extend(re.findall(pattern=pattern, string=str(file)))
    logger.info(msg=f'Extracted archives for the following repositories {repo_names}')
    return repo_names


if __name__ == '__main__':
    from mkdocs_multisource_docs.src.constants import TEST_APPLICATION_CONF

    corpus_manager = CorpusManager(
        artifacts_path=TMP_FOLDER_PATH,
        application_config=get_application_config(config_path=TEST_APPLICATION_CONF)
    )
    corpus_manager.extract_documentation_from_artifacts()
