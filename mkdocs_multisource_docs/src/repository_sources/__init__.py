"""Repository source implementations."""

from pathlib import Path

from mkdocs_multisource_docs.src.config import AppConfig
from mkdocs_multisource_docs.src.repository_sources.base import RepositorySource
from mkdocs_multisource_docs.src.repository_sources.gitlab import GitLabRepositorySource
from mkdocs_multisource_docs.src.repository_sources.local import LocalRepositorySource


def create_repository_source(
    application_config: AppConfig,
    config_path: Path,
) -> RepositorySource:
    """Create the repository provider selected in the application configuration."""
    if application_config.SOURCE == "local":
        return LocalRepositorySource(
            application_config=application_config,
            config_directory=config_path.parent,
        )

    return GitLabRepositorySource(application_config=application_config)


__all__ = [
    "GitLabRepositorySource",
    "LocalRepositorySource",
    "RepositorySource",
    "create_repository_source",
]
