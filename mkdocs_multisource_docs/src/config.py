"""
Application configuration
"""

import json
import logging
from pathlib import Path
from pprint import pprint

from pydantic import BaseModel

logger = logging.getLogger(__name__)


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
    GENERATE_INDEX: bool = False  # by default do not generate index.md file for docs


def get_application_config(config_path: Path) -> AppConfig:
    """
    Fills application config DTO from json file
    :param config_path: path to configuration file
    :return: AppConfig object with all fields filled
    """
    logger.info('Getting application configuration file %s', config_path)
    with open(file=config_path, mode='r', encoding='utf-8') as file:
        return AppConfig(**json.load(fp=file))


if __name__ == '__main__':
    from mkdocs_multisource_docs.src.constants import TEST_APPLICATION_CONF
    app_config = get_application_config(config_path=TEST_APPLICATION_CONF)
    pprint(app_config)
