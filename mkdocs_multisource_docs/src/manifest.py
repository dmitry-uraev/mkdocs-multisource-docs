"""Manifest of documentation files collected from source repositories."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath

from mkdocs_multisource_docs.src.config import AppConfig

MANIFEST_FILENAME = ".multisource-manifest.json"


class DocumentManifest:
    """Map source repository paths to their URLs in the generated site."""

    def __init__(self, documents: dict[str, str]) -> None:
        self.documents = documents

    @classmethod
    def build(cls, build_folder: Path, application_config: AppConfig) -> DocumentManifest:
        """Build a manifest from the cloned repositories in ``build_folder``.

        Source paths use the same syntax as ``multisource-ref``:
        ``repository:path``. Markdown files below ``docs_root`` are exposed
        below ``repository/docs`` in the generated site. Keeping this mapping
        in a manifest makes link resolution independent from the external URL
        used in the source Markdown.
        """
        documents: dict[str, str] = {}

        for repository in application_config.DOCS_REPOSITORIES:
            source_root = build_folder / repository.name / repository.docs_root
            if not source_root.is_dir():
                continue

            for source_file in source_root.rglob("*.md"):
                relative_path = source_file.relative_to(source_root)
                source_path = PurePosixPath(repository.docs_root) / relative_path
                source_key = f"{repository.name}:{source_path.as_posix()}"
                site_path = PurePosixPath("/", repository.name, "docs") / relative_path
                site_url = site_path.with_suffix(".html").as_posix()
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
