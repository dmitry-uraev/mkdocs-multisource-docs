import json
import tempfile
import unittest
from pathlib import Path

from mkdocs_multisource_docs.src.config import AppConfig, DocRepository, LocalSourceConfig
from mkdocs_multisource_docs.src.manifest import DocumentManifest


class DocumentManifestTest(unittest.TestCase):
    def test_build_maps_docs_root_to_site_url(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            build_folder = Path(temporary_directory)
            document = build_folder / "example-repo" / "docs" / "HOWTO" / "naming_metrics.md"
            document.parent.mkdir(parents=True)
            document.write_text("# Naming metrics\n", encoding="utf-8")

            config = AppConfig(
                repositories=[
                    DocRepository(
                        name="example-repo",
                        source=LocalSourceConfig(type="local", path="."),
                        branch="develop",
                        docs_root="docs",
                    )
                ],
            )

            manifest = DocumentManifest.build(build_folder, config)

            self.assertEqual(
                manifest.documents,
                {
                    "example-repo:docs/HOWTO/naming_metrics.md": (
                        "/example-repo/docs/HOWTO/naming_metrics.html"
                    )
                },
            )

    def test_build_maps_readme_to_index(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            build_folder = Path(temporary_directory)
            document = build_folder / "example-repo" / "README.md"
            document.parent.mkdir(parents=True)
            document.write_text("# Example repository\n", encoding="utf-8")

            config = AppConfig(
                repositories=[
                    DocRepository(
                        name="example-repo",
                        source=LocalSourceConfig(type="local", path="."),
                    )
                ],
            )

            manifest = DocumentManifest.build(build_folder, config)

            self.assertEqual(
                manifest.documents["example-repo:README.md"],
                "/example-repo/index.html",
            )

    def test_build_preserves_hidden_docs_root(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            build_folder = Path(temporary_directory)
            document = build_folder / "example-repo" / ".docs" / "guide.md"
            document.parent.mkdir(parents=True)
            document.write_text("# Guide\n\n[Reference](reference.html)\n", encoding="utf-8")
            resource = build_folder / "example-repo" / ".docs" / "reference.html"
            resource.write_text("<h1>Guide</h1>\n", encoding="utf-8")

            config = AppConfig(
                repositories=[
                    DocRepository(
                        name="example-repo",
                        source=LocalSourceConfig(type="local", path="."),
                        branch="main",
                        docs_root=".docs",
                    )
                ],
            )

            manifest = DocumentManifest.build(build_folder, config)

            self.assertEqual(
                manifest.documents["example-repo:.docs/guide.md"],
                "/example-repo/.docs/guide.html",
            )
            self.assertEqual(
                manifest.documents["example-repo:.docs/reference.html"],
                "/example-repo/.docs/reference.html",
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
