"""Manifest of documentation files collected from source repositories."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath

from mkdocs_multisource_docs.src.config import AppConfig
from mkdocs_multisource_docs.src.file_collection import collect_repository_files

MANIFEST_FILENAME = ".multisource-manifest.json"


class DocumentManifest:
    """Map source repository paths to their URLs in the generated site."""

    def __init__(self, documents: dict[str, str]) -> None:
        self.documents = documents

    @classmethod
    def build(cls, build_folder: Path, application_config: AppConfig) -> DocumentManifest:
        """Build a manifest from the cloned repositories in ``build_folder``.

        Source paths use the same syntax as ``multisource-ref``:
        ``repository:path``. Markdown pages and their collected resources are
        exposed below the same repository-relative path in the generated site.
        Keeping this mapping in a manifest makes link resolution independent
        from the external URL used in the source Markdown.
        """
        documents: dict[str, str] = {}
        build_folder = build_folder.resolve()

        repositories = {
            repository.name: repository for repository in application_config.repositories
        }
        for source_file in collect_repository_files(build_folder, application_config):
            repository_name = source_file.relative_to(build_folder).parts[0]
            repository = repositories[repository_name]
            relative_path = source_file.relative_to(build_folder / repository.name)
            source_key = f"{repository.name}:{relative_path.as_posix()}"
            site_path = PurePosixPath("/", repository.name) / relative_path
            if source_file.suffix.lower() == ".md":
                output_name = (
                    "index.html" if source_file.stem == "README" else f"{source_file.stem}.html"
                )
                site_url = site_path.with_name(output_name).as_posix()
            else:
                site_url = site_path.as_posix()
            documents[source_key] = site_url

        return cls(documents=documents)

    def write(self, path: Path) -> None:
        """Write the manifest as deterministic, human-readable JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {"version": 1, "documents": dict(sorted(self.documents.items()))},
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
