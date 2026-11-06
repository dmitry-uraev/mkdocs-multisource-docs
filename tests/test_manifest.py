import json
import tempfile
import unittest
from pathlib import Path

from mkdocs_multisource_docs.src.config import AppConfig, DocRepository
from mkdocs_multisource_docs.src.manifest import DocumentManifest


class DocumentManifestTest(unittest.TestCase):
    def test_build_maps_docs_root_to_site_url(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            build_folder = Path(temporary_directory)
            document = build_folder / "example-repo" / "docs" / "HOWTO" / "naming_metrics.md"
            document.parent.mkdir(parents=True)
            document.write_text("# Naming metrics\n", encoding="utf-8")

            config = AppConfig(
                GIT_HOST="https://gitlab.example.com",
                GIT_READ_TOKEN="token",
                DOCS_REPOSITORIES=[DocRepository(
                    name="example-repo",
                    repo_id=1,
                    branch="develop",
                    docs_root="docs",
                )],
                EXCLUDE_IMAGES=[],
            )

            manifest = DocumentManifest.build(build_folder, config)

            self.assertEqual(
                manifest.documents,
                {"example-repo:docs/HOWTO/naming_metrics.md":
                 "/example-repo/docs/HOWTO/naming_metrics.html"},
            )

    def test_build_normalizes_hidden_docs_root(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            build_folder = Path(temporary_directory)
            document = build_folder / "example-repo" / ".docs" / "guide.md"
            document.parent.mkdir(parents=True)
            document.write_text("# Guide\n", encoding="utf-8")

            config = AppConfig(
                GIT_HOST="https://gitlab.example.com",
                GIT_READ_TOKEN="token",
                DOCS_REPOSITORIES=[DocRepository(
                    name="example-repo",
                    repo_id=1,
                    branch="main",
                    docs_root=".docs",
                )],
                EXCLUDE_IMAGES=[],
            )

            manifest = DocumentManifest.build(build_folder, config)

            self.assertEqual(
                manifest.documents["example-repo:.docs/guide.md"],
                "/example-repo/docs/guide.html",
            )

    def test_write_uses_manifest_schema(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "manifest.json"
            DocumentManifest({"repo:docs/index.md": "/repo/docs/index.html"}).write(path)

            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                {
                    "version": 1,
                    "documents": {"repo:docs/index.md": "/repo/docs/index.html"},
                },
            )


if __name__ == "__main__":
    unittest.main()
