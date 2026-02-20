"""
Useful functions to work with GitLab repositories using python-gitlab
"""

import logging
from pathlib import Path
import shutil
import subprocess
from typing import Any
from urllib.parse import urlparse, urlunparse

from gitlab import Gitlab
from gitlab.v4.objects import Project

from mkdocs_multisource_docs.src.config import (AppConfig, DocRepository,
                                                get_application_config)
from mkdocs_multisource_docs.src.constants import TMP_FOLDER_PATH

logger = logging.getLogger(__name__)


class GitLabManager:

    """
    Encapsulates GitLab management logic

    Connects to GitLab
    Downloads repositories specified in application config into TMP_FOLDER_PATH
    """

    def __init__(self, application_config: AppConfig) -> None:
        self.__config = application_config
        self.__gitlab = self.__initialize_gitlab_manager()

        self.__docs_list = [doc_repo.name for doc_repo in self.__config.DOCS_REPOSITORIES]
        self.__docs_ids = [doc_repo.repo_id for doc_repo in self.__config.DOCS_REPOSITORIES]

        self.__docs_map: dict[str, DocRepository] = {
            doc_repo.name: doc_repo for doc_repo in self.__config.DOCS_REPOSITORIES}


    def __initialize_gitlab_manager(self) -> Gitlab:
        """
        Initializes GitLab object of python-gitlab library
        :return: initialized Gitlab object
        """
        logger.info('Initializing GitLab connection for %s', self.__config.GIT_HOST)
        return Gitlab(url=self.__config.GIT_HOST, private_token=self.__config.GIT_READ_TOKEN)

    def get_gitlab_repositories(self) -> list[Project | Any]:
        """
        Returns a list of Project objects (that is GitLab repositories)
        :return: List of gitlab.v4.objects.Project instances
        """
        _ = [project for project in self.__gitlab.projects.list(iterator=True)
             if project.name in self.__docs_list and project.id in self.__docs_ids]
        logger.info('Got gitlab repositories according to application config %s', _)
        return _

    def clone_gitlab_repositories(self, repositories: list[Project], clone_path: Path) -> None:
        """
        Clone repositories into the folder specified
        :param repositories: a list of Project object instances
        :param clone_path: destination path for cloning
        :return: None
        """
        logger.info(f"Cloning gitlab repositories into {TMP_FOLDER_PATH}")
        for repo in repositories:
            self._clone_gitlab_repository(repository=repo, clone_path=clone_path)

    def _clone_gitlab_repository(self, repository: Project, clone_path: Path) -> None:
        """
        Clone repository using git clone command
        :param repository: Project object instance
        :param clone_path: destination path for cloning
        :return: None
        """
        # check path exists
        if not clone_path.exists():
            clone_path.mkdir(parents=True)

        repo_destination = clone_path / repository.name

        # remove if repo destination already exists
        if repo_destination.exists():
            logger.info(f'Removing existing directory: {repo_destination}')
            shutil.rmtree(repo_destination)

        # form repository url with authentication
        repo_url: str = repository.http_url_to_repo
        parsed_url = urlparse(repo_url)
        authenticated_url = urlunparse((
            parsed_url.scheme,
            f"oauth2:{self.__config.GIT_READ_TOKEN}@{parsed_url.netloc}",
            parsed_url.path,
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment
        ))

        # get branch information from config
        doc_config = self.__docs_map.get(repository.name)
        branch_name = doc_config.branch if doc_config and doc_config.branch else "main"

        # build git clone command
        clone_cmd = [
            "git", "clone",
            "--branch", branch_name,
            "--depth", "1",
            authenticated_url,
            str(repo_destination)
        ]

        logger.info(f"Cloning repository {repository.name} from branch {branch_name}")

        try:
            result = subprocess.run(
                clone_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Successfully cloned {repository.name}: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to clone {repository.name}: {e.stderr}")
            raise

    def download_gitlab_repositories(
            self, repositories: list[Project], download_path: Path) -> None:
        """
        DEPRECATED. Download repositories as zip archives into the folder specified
        :param repositories: a list of Project object instances
        :param download_path: destination path is the same for all repositories
        :return: None
        """
        logger.info(msg=f'Downloading gitlab repositories into {TMP_FOLDER_PATH}')
        # map(lambda x: self._download_gitlab_repository(
        # x, download_path, name=f'export_{x.name}.zip'), repositories)
        for repo in repositories:
            self._download_gitlab_repository(
               repository=repo, download_path=download_path, name=f'export_{repo.name}.zip')

    def _download_gitlab_repository(
            self, repository: Project, download_path: Path, name: str = 'export.zip') -> None:
        """
        DEPRECATED. Download repository as zip archive
        :param repository: Project object instance
        :param download_path: destination path
        :param name: optional name for the archive, by default is export.tgz
        :return: None
        """
        if not download_path.exists():
            download_path.mkdir(parents=True)
        download_path = download_path / name
        if download_path.exists():
            return

        with open(file=download_path, mode='wb') as file:
            branch_name = self.__docs_map.get(repository.name)
            match branch_name:
                case None: repository.repository_archive(
                    format='zip', streamed=True, action=file.write)
                case _: repository.repository_archive(sha=branch_name.branch,
                    format='zip', streamed=True, action=file.write)


if __name__ == '__main__':
    from mkdocs_multisource_docs.src.constants import TEST_APPLICATION_CONF
    git_manager = GitLabManager(application_config=get_application_config(TEST_APPLICATION_CONF))
    repos = git_manager.get_gitlab_repositories()
    git_manager.clone_gitlab_repositories(repositories=repos, clone_path=TMP_FOLDER_PATH)
