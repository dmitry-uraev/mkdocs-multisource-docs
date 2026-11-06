"""GitLab repository source."""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

from gitlab import Gitlab
from gitlab.v4.objects import Project

from mkdocs_multisource_docs.src.config import AppConfig
from mkdocs_multisource_docs.src.constants import TMP_FOLDER_PATH

logger = logging.getLogger(__name__)


class GitLabRepositorySource:
    """Collect and clone repositories from GitLab."""

    def __init__(self, application_config: AppConfig) -> None:
        self._config = application_config
        self._gitlab = self._initialize_gitlab()
        self._docs_list = [repo.name for repo in self._config.DOCS_REPOSITORIES]
        self._docs_ids = [repo.repo_id for repo in self._config.DOCS_REPOSITORIES]
        self._docs_map = {
            repository.name: repository for repository in self._config.DOCS_REPOSITORIES
        }

    def _initialize_gitlab(self) -> Gitlab:
        """Initialize the python-gitlab client."""
        logger.info("Initializing GitLab connection for %s", self._config.GIT_HOST)
        return Gitlab(url=self._config.GIT_HOST, private_token=self._config.GIT_READ_TOKEN)

    def get_repositories(self) -> list[Project | Any]:
        """Return repositories selected by the application configuration."""
        repositories = [
            project
            for project in self._gitlab.projects.list(iterator=True)
            if project.name in self._docs_list and project.id in self._docs_ids
        ]
        logger.info("Got GitLab repositories according to application config %s", repositories)
        return repositories

    def clone_repositories(self, repositories: list[Project], clone_path: Path) -> None:
        """Clone repositories into the common build directory."""
        logger.info("Cloning GitLab repositories into %s", TMP_FOLDER_PATH)
        for repository in repositories:
            self._clone_repository(repository=repository, clone_path=clone_path)

    def _clone_repository(self, repository: Project, clone_path: Path) -> None:
        """Clone one GitLab repository."""
        clone_path.mkdir(parents=True, exist_ok=True)
        repository_destination = clone_path / repository.name

        if repository_destination.exists():
            logger.info("Removing existing directory: %s", repository_destination)
            shutil.rmtree(repository_destination)

        repository_url: str = repository.http_url_to_repo
        parsed_url = urlparse(repository_url)
        authenticated_url = urlunparse(
            (
                parsed_url.scheme,
                f"oauth2:{self._config.GIT_READ_TOKEN}@{parsed_url.netloc}",
                parsed_url.path,
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment,
            )
        )

        repository_config = self._docs_map.get(repository.name)
        branch_name = (
            repository_config.branch if repository_config and repository_config.branch else "main"
        )
        clone_command = [
            "git",
            "clone",
            "--branch",
            branch_name,
            "--depth",
            "1",
            authenticated_url,
            str(repository_destination),
        ]

        logger.info("Cloning repository %s from branch %s", repository.name, branch_name)
        try:
            result = subprocess.run(clone_command, capture_output=True, text=True, check=True)
            logger.info("Successfully cloned %s: %s", repository.name, result.stdout)
        except subprocess.CalledProcessError as error:
            logger.error("Failed to clone %s: %s", repository.name, error.stderr)
            raise

    def download_repositories(self, repositories: list[Project], download_path: Path) -> None:
        """Download repositories as zip archives for the legacy workflow."""
        logger.info("Downloading GitLab repositories into %s", TMP_FOLDER_PATH)
        for repository in repositories:
            self._download_repository(
                repository=repository,
                download_path=download_path,
                name=f"export_{repository.name}.zip",
            )

    def _download_repository(
        self,
        repository: Project,
        download_path: Path,
        name: str = "export.zip",
    ) -> None:
        """Download one repository as a zip archive."""
        download_path.mkdir(parents=True, exist_ok=True)
        archive_path = download_path / name
        if archive_path.exists():
            return

        with open(file=archive_path, mode="wb") as archive:
            repository_config = self._docs_map.get(repository.name)
            if repository_config is None:
                repository.repository_archive(format="zip", streamed=True, action=archive.write)
            else:
                repository.repository_archive(
                    sha=repository_config.branch,
                    format="zip",
                    streamed=True,
                    action=archive.write,
                )
