"""
Useful functions to work with GitLab repositories using python-gitlab
"""

import logging

from pathlib import Path
from typing import Any

from gitlab import Gitlab
from gitlab.v4.objects import Project

from mkdocs_multisource_docs.src.constants import TMP_FOLDER_PATH
from mkdocs_multisource_docs.src.config import AppConfig, get_application_config
from mkdocs_multisource_docs.src.utils import setup_logger


logger = setup_logger(name=__name__, level=logging.DEBUG)


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

    def download_gitlab_repositories(
            self, repositories: list[Project], download_path: Path) -> None:
        """
        Download repositories as zip archives into the folder specified
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

    @staticmethod
    def _download_gitlab_repository(
        repository: Project, download_path: Path, name: str = 'export.zip') -> None:
        """
        Download repository as zip archive
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
            repository.repository_archive(format='zip', streamed=True, action=file.write)


if __name__ == '__main__':

    from mkdocs_multisource_docs.src.constants import TEST_APPLICATION_CONF
    git_manager = GitLabManager(application_config=get_application_config(TEST_APPLICATION_CONF))
    repos = git_manager.get_gitlab_repositories()
    git_manager.download_gitlab_repositories(repositories=repos, download_path=TMP_FOLDER_PATH)
