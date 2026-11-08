"""Repository source implementations and factory."""

import json
from pathlib import Path

from mkdocs_multisource_docs.src.config import AppConfig, DocRepository, GitHubSourceConfig
from mkdocs_multisource_docs.src.repository_sources.base import RepositorySource
from mkdocs_multisource_docs.src.repository_sources.gitlab import GitLabRepositorySource
from mkdocs_multisource_docs.src.repository_sources.local import LocalRepositorySource


def create_repository_sources(
    application_config: AppConfig,
    config_path: Path,
) -> list[RepositorySource]:
    """Create one source instance for each distinct source configuration."""
    grouped: dict[str, list[DocRepository]] = {}
    for repository in application_config.repositories:
        source_data = repository.source.model_dump()
        if source_data["type"] == "gitlab":
            source_data.pop("project_id")
        elif source_data["type"] == "github":
            source_data.pop("repository")
        key = json.dumps(source_data, sort_keys=True)
        grouped.setdefault(key, []).append(repository)

    sources: list[RepositorySource] = []
    for repositories in grouped.values():
        source = repositories[0].source
        if isinstance(source, GitHubSourceConfig):
            raise NotImplementedError("GitHub repository source is not implemented yet")
        if source.type == "gitlab":
            sources.append(GitLabRepositorySource(repositories=repositories))
        else:
            sources.append(
                LocalRepositorySource(
                    repositories=repositories,
                    config_directory=config_path.parent,
                )
            )

    return sources


__all__ = [
    "GitLabRepositorySource",
    "LocalRepositorySource",
    "RepositorySource",
    "create_repository_sources",
]
