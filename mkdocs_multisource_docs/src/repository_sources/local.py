"""Local filesystem repository source."""

import logging
import shutil
from pathlib import Path

from mkdocs_multisource_docs.src.config import AppConfig, DocRepository

logger = logging.getLogger(__name__)


class LocalRepositorySource:
    """Use directories on disk as repository sources for demos and tests."""

    def __init__(self, application_config: AppConfig, config_directory: Path) -> None:
        self._config = application_config
        self._source_root = (config_directory / application_config.LOCAL_SOURCE_PATH).resolve()

    def get_repositories(self) -> list[DocRepository]:
        """Return configured local repositories without accessing the network."""
        if not self._source_root.is_dir():
            raise FileNotFoundError(f"Local repository source not found: {self._source_root}")

        for repository in self._config.DOCS_REPOSITORIES:
            repository_path = self._source_root / repository.name
            if not repository_path.is_dir():
                raise FileNotFoundError(f"Local repository not found: {repository_path}")

            docs_path = repository_path / repository.docs_root
            if not docs_path.is_dir():
                raise FileNotFoundError(f"Documentation root not found: {docs_path}")

        logger.info(
            "Found %s local repositories in %s",
            len(self._config.DOCS_REPOSITORIES),
            self._source_root,
        )
        return self._config.DOCS_REPOSITORIES

    def clone_repositories(self, repositories: list[DocRepository], clone_path: Path) -> None:
        """Copy configured local repositories into the common build directory."""
        clone_path.mkdir(parents=True, exist_ok=True)
        for repository in repositories:
            source_path = self._source_root / repository.name
            destination_path = clone_path / repository.name

            if destination_path.exists():
                logger.info("Removing existing local repository directory: %s", destination_path)
                shutil.rmtree(destination_path)

            logger.info("Copying local repository %s", repository.name)
            shutil.copytree(source_path, destination_path)
