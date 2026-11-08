"""Local filesystem repository source."""

import logging
import shutil
from pathlib import Path

from mkdocs_multisource_docs.src.config import DocRepository, LocalSourceConfig

logger = logging.getLogger(__name__)


class LocalRepositorySource:
    """Use directories on disk as repository sources for demos and tests."""

    def __init__(self, repositories: list[DocRepository], config_directory: Path) -> None:
        self._repositories = repositories
        self._config_directory = config_directory

    def _source_path(self, repository: DocRepository) -> Path:
        if not isinstance(repository.source, LocalSourceConfig):
            raise ValueError("Local source requires a local repository configuration")
        return (self._config_directory / repository.source.path / repository.name).resolve()

    def get_repositories(self) -> list[DocRepository]:
        """Return configured local repositories without accessing the network."""
        for repository in self._repositories:
            repository_path = self._source_path(repository)
            if not repository_path.is_dir():
                raise FileNotFoundError(f"Local repository not found: {repository_path}")

            docs_path = repository_path / repository.docs_root
            if not docs_path.is_dir():
                raise FileNotFoundError(f"Documentation root not found: {docs_path}")

        logger.info("Found %s local repositories", len(self._repositories))
        return self._repositories

    def clone_repositories(self, repositories: list[DocRepository], clone_path: Path) -> None:
        """Copy configured local repositories into the common build directory."""
        clone_path.mkdir(parents=True, exist_ok=True)
        for repository in repositories:
            source_path = self._source_path(repository)
            destination_path = clone_path / repository.name

            if destination_path.exists():
                logger.info("Removing existing local repository directory: %s", destination_path)
                shutil.rmtree(destination_path)

            logger.info("Copying local repository %s", repository.name)
            shutil.copytree(source_path, destination_path)
