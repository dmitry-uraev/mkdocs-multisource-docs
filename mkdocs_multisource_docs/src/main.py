"""
Entrypoint module for application
"""

from pathlib import Path

from mkdocs_multisource_docs.src.builders.javadoc import build_javadocs
from mkdocs_multisource_docs.src.config import AppConfig, get_demo_application_config
from mkdocs_multisource_docs.src.constants import BUILD_FOLDER_PATH
from mkdocs_multisource_docs.src.manifest import MANIFEST_FILENAME, DocumentManifest
from mkdocs_multisource_docs.src.md_utils import MarkdownProcessing
from mkdocs_multisource_docs.src.repository_sources import create_repository_sources


def main(application_config: AppConfig, config_path: Path) -> None:
    """
    Multisource processing entrypoint
    """

    # repository source
    for repository_source in create_repository_sources(
        application_config=application_config,
        config_path=config_path,
    ):
        doc_repositories = repository_source.get_repositories()
        repository_source.clone_repositories(
            repositories=doc_repositories,
            clone_path=BUILD_FOLDER_PATH,
        )

    # DEPRECATED. corpus_manager.py
    # corpus = CorpusManager(artifacts_path=TMP_FOLDER_PATH, application_config=config)
    # corpus.extract_documentation_from_artifacts()

    # md_utils.py
    md_manager = MarkdownProcessing(
        application_config=application_config,
        docs_folder=BUILD_FOLDER_PATH,
    )
    md_manager.process_doc_folder()

    manifest = DocumentManifest.build(
        build_folder=BUILD_FOLDER_PATH,
        application_config=application_config,
    )
    manifest.write(BUILD_FOLDER_PATH / MANIFEST_FILENAME)

    # Javadocs
    build_javadocs(app_conf=application_config)


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    main(
        application_config=get_demo_application_config(),
        config_path=project_root / "examples" / "demo" / "mkdocs.yml",
    )
