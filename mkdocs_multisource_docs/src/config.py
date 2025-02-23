"""
Application configuration
"""

import json
import logging

from pprint import pprint
from pathlib import Path
from pydantic import BaseModel

from mkdocs_multisource_docs.src.utils import setup_logger


logger = setup_logger(name=__name__, level=logging.DEBUG)


class DocRepository(BaseModel):
    """
    Documentation repo DTO
    """

    name: str
    repo_id: int
    branch: str


class AppConfig(BaseModel):
    """
    Application config DTO
    """

    GIT_HOST: str
    GIT_READ_TOKEN: str
    DOCS_REPOSITORIES: list[DocRepository]
    EXCLUDE_IMAGES: list[str]


def get_application_config(config_path: Path) -> AppConfig:
    """
    Fills application config DTO from json file
    :param config_path: path to configuration file
    :return: AppConfig object with all fields filled
    """
    logger.info('[INFO] Getting application configuration file %s', config_path)
    with open(file=config_path, mode='r', encoding='utf-8') as file:
        return AppConfig(**json.load(fp=file))


if __name__ == '__main__':
    from mkdocs_multisource_docs.src.constants import TEST_APPLICATION_CONF
    app_config = get_application_config(config_path=TEST_APPLICATION_CONF)
    pprint(app_config)
