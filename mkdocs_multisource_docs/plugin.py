"""MkDocs plugin entrypoint."""

import logging
import os
import shutil
from fnmatch import fnmatch
from pathlib import Path

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File

from mkdocs_multisource_docs.src.config import application_config_from_data
from mkdocs_multisource_docs.src.constants import (
    BUILD_FOLDER_PATH,
    JAVADOC_FOLDER_PATH,
    TMP_FOLDER_PATH,
)
from mkdocs_multisource_docs.src.logs import setup_root_logger
from mkdocs_multisource_docs.src.main import main
from mkdocs_multisource_docs.src.manifest import MANIFEST_FILENAME

logger = logging.getLogger(__name__)


class MultiSourceCollect(BasePlugin):
    """Collect additional documentation from configured repositories."""

    config_scheme = [
        ("repositories", config_options.Type(list, default=[])),
        ("exclude_images", config_options.Type(list, default=[])),
        ("generate_index", config_options.Type(bool, default=False)),
        ("navigation", config_options.Type(dict, default={})),
    ]

    setup_root_logger()

    def on_config(self, config):
        """Validate and normalize inline plugin configuration."""
        self._application_config = application_config_from_data(
            {
                "repositories": self.config["repositories"],
                "exclude_images": self.config["exclude_images"],
                "generate_index": self.config["generate_index"],
                "navigation": self.config["navigation"],
            }
        )
        if not self._application_config.repositories:
            raise ValueError("At least one repository must be configured")
        self._config_path = Path(config.config_file_path)

        logger.info("Loaded multisource plugin configuration")
        return config

    def on_files(self, files, *, config):
        """Collect source files and add them to the MkDocs file collection."""
        main(
            application_config=self._application_config,
            config_path=self._config_path,
        )

        for root, _, filenames in os.walk(BUILD_FOLDER_PATH):
            for filename in filenames:
                file_path = Path(root) / filename
                if file_path.name == MANIFEST_FILENAME:
                    continue
                relative_path = file_path.relative_to(BUILD_FOLDER_PATH)
                files.append(
                    File(
                        path=str(relative_path),
                        src_dir=str(BUILD_FOLDER_PATH),
                        dest_dir=config["site_dir"],
                        use_directory_urls=config["use_directory_urls"],
                    )
                )

        if self._application_config.navigation.mode == "auto":
            self._configure_generated_navigation(config)
        return files

    def _configure_generated_navigation(self, config) -> None:
        """Add collected repository pages to MkDocs navigation."""
        repository_entries: list[dict] = []
        for repository in sorted(
            self._application_config.repositories,
            key=lambda item: item.navigation.order,
        ):
            navigation = repository.navigation
            if not navigation.enabled:
                continue

            docs_root = BUILD_FOLDER_PATH / repository.name / repository.docs_root
            index_path = Path(repository.navigation.index or "index.md")
            pages: list[dict] = []
            for source_file in sorted(docs_root.rglob("*.md")):
                relative_path = source_file.relative_to(docs_root)
                relative_name = relative_path.as_posix()
                if navigation.include and not any(
                    fnmatch(relative_name, pattern) for pattern in navigation.include
                ):
                    continue
                if any(fnmatch(relative_name, pattern) for pattern in navigation.exclude):
                    continue

                site_path = Path(repository.name) / repository.docs_root / relative_path
                label = source_file.stem.replace("_", " ").replace("-", " ").title()
                if relative_path == index_path:
                    label = navigation.title or repository.name
                pages.append({label: site_path.as_posix()})

            if not pages:
                continue
            if len(pages) == 1 and pages[0].keys() == {navigation.title or repository.name}:
                repository_entries.append(pages[0])
            else:
                repository_entries.append({navigation.title or repository.name: pages})

        if not repository_entries:
            return

        navigation_section: dict = {
            self._application_config.navigation.title: repository_entries,
        }
        current_nav = list(config.get("nav") or [])
        if self._application_config.navigation.position == "before":
            config["nav"] = [navigation_section, *current_nav]
        else:
            config["nav"] = [*current_nav, navigation_section]

    def on_post_build(self, *, config):
        """Remove intermediate build files after the site is built."""
        self._cleanup_intermediate_files(remove_javadoc=False)

        if JAVADOC_FOLDER_PATH.exists():
            javadoc_dest = Path(config["site_dir"]) / "apidocs"
            shutil.copytree(JAVADOC_FOLDER_PATH, javadoc_dest, dirs_exist_ok=True)
        self._cleanup_intermediate_files(remove_javadoc=True)

    def on_build_error(self, error):
        """Remove intermediate files when MkDocs aborts the build."""
        logger.error("MkDocs build failed: %s", error)
        self._cleanup_intermediate_files(remove_javadoc=True)

    @staticmethod
    def _cleanup_intermediate_files(*, remove_javadoc: bool) -> None:
        """Remove directories created by the plugin during a build."""
        paths = [BUILD_FOLDER_PATH, TMP_FOLDER_PATH]
        if remove_javadoc:
            paths.append(JAVADOC_FOLDER_PATH)

        for path in paths:
            try:
                if path.exists():
                    shutil.rmtree(path)
            except OSError as cleanup_error:
                logger.warning(
                    "Could not remove intermediate directory %s: %s", path, cleanup_error
                )
