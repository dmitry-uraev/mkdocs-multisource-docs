"""
Plugin entrypoint
"""

import json
import os
import shutil
from pathlib import Path

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File

from mkdocs_multisource_docs.src.constants import (BUILD_FOLDER_PATH,
                                                   JAVADOC_FOLDER_PATH)
from mkdocs_multisource_docs.src.logs import setup_root_logger
from mkdocs_multisource_docs.src.main import main


class MultiSourceCollect(BasePlugin):
    """
    Collect additional documentation from repositories configured
    """
    config_scheme = [
        ('multisource_config', config_options.Type(str, default=''))
    ]

    setup_root_logger()

    def on_config(self, config,):
        """
        Make sure configuration file exists anf formed properly
        """
        config_file = self.config['multisource_config']
        if not config_file:
            raise ValueError("multisource_config parameter is not specified in mkdocs.yml")

        if not os.path.exists(config_file):
            raise FileNotFoundError(f"File '{config_file}' is not found")

        try:
            with open(file=config_file, mode='r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f'File "{config_file}" includes incorrect JSON. Error {e}') from e

        print("Found plugin config at:", self.config['multisource_config'])
        return config

    def on_files(self, files, *, config):
        """
        Call main plugin logic
        """
        main(app_cfg=self.config['multisource_config'])

        allowed_extensions = {'.md', '.jpeg', '.jpg', '.png'}
        for root, _, filenames in os.walk(BUILD_FOLDER_PATH):
            for filename in filenames:
                file_path = Path(root) / filename
                if file_path.suffix.lower() in allowed_extensions or file_path.name == '.pages':
                    relative_path = file_path.relative_to(BUILD_FOLDER_PATH)
                    files.append(File(
                        path=str(relative_path),
                        src_dir=str(BUILD_FOLDER_PATH),
                        dest_dir=config['site_dir'],
                        use_directory_urls=config['use_directory_urls']
                    ))
        return files

    def on_post_build(self, *, config):
        """
        Remove intermidiate build files after build completed
        """
        if os.path.exists(BUILD_FOLDER_PATH):
            shutil.rmtree(BUILD_FOLDER_PATH)

        # Javadocs
        if JAVADOC_FOLDER_PATH.exists():
            javadoc_dest = Path(config['site_dir']) / 'apidocs'
            shutil.copytree(
                JAVADOC_FOLDER_PATH,
                javadoc_dest,
                dirs_exist_ok=True
            )
            shutil.rmtree(JAVADOC_FOLDER_PATH)
