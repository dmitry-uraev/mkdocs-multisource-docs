"""
Entrypoint module for application
"""

import logging
from pathlib import Path

from mkdocs_multisource_docs.src.builders.javadoc import build_javadocs
from mkdocs_multisource_docs.src.config import get_application_config
from mkdocs_multisource_docs.src.constants import (BUILD_FOLDER_PATH,
                                                   TMP_FOLDER_PATH)
from mkdocs_multisource_docs.src.corpus_manager import CorpusManager
from mkdocs_multisource_docs.src.gitlab_utils import GitLabManager
from mkdocs_multisource_docs.src.md_utils import MarkdownProcessing

logger = logging.getLogger(__name__)


def main(app_cfg: str | Path) -> None:
    """
    Multisource processing entrypoint
    """

    # config.py
    config = get_application_config(config_path=Path(app_cfg))

    # gitlab_utils.py
    gitlab = GitLabManager(application_config=config)
    doc_repositories = gitlab.get_gitlab_repositories()
    gitlab.download_gitlab_repositories(
        repositories=doc_repositories, download_path=TMP_FOLDER_PATH)

    # corpus_manager.py
    corpus = CorpusManager(artifacts_path=TMP_FOLDER_PATH, application_config=config)
    corpus.extract_documentation_from_artifacts()

    # md_utils.py
    md_manager = MarkdownProcessing(application_config=config, docs_folder=BUILD_FOLDER_PATH)
    md_manager.process_doc_folder()

    # Javadocs
    build_javadocs(app_conf=config)


if __name__ == '__main__':

    from mkdocs_multisource_docs.src.constants import TEST_APPLICATION_CONF
    main(TEST_APPLICATION_CONF)
