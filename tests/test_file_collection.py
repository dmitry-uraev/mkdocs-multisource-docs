import tempfile
import unittest
from pathlib import Path

from mkdocs_multisource_docs.src.config import AppConfig, DocRepository, LocalSourceConfig
from mkdocs_multisource_docs.src.file_collection import collect_repository_files


class RepositoryFileCollectionTest(unittest.TestCase):
    def test_collects_markdown_and_referenced_resources_only(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            build_folder = Path(temporary_directory)
            repository_root = (build_folder / "example-repo").resolve()
            docs_root = repository_root / "docs"
            (docs_root / "assets").mkdir(parents=True)
            (repository_root / "shared").mkdir()

            entrypoint = docs_root / "index.md"
            entrypoint.write_text(
                "![Diagram](assets/diagram.svg)\n\n[Schema](../shared/schema.json)\n",
                encoding="utf-8",
            )
            referenced_image = docs_root / "assets" / "diagram.svg"
            referenced_image.write_text("<svg />\n", encoding="utf-8")
            referenced_schema = repository_root / "shared" / "schema.json"
            referenced_schema.write_text("{}\n", encoding="utf-8")
            (docs_root / "unused.txt").write_text("unused\n", encoding="utf-8")
            (repository_root / "pom.xml").write_text("<project />\n", encoding="utf-8")

            config = AppConfig(
                repositories=[
                    DocRepository(
                        name="example-repo",
                        source=LocalSourceConfig(type="local", path="."),
                        docs_root="docs",
                    )
                ]
            )

            collected = collect_repository_files(build_folder, config)

            self.assertEqual(
                {path.relative_to(repository_root).as_posix() for path in collected},
                {"docs/index.md", "docs/assets/diagram.svg", "shared/schema.json"},
            )


if __name__ == "__main__":
    unittest.main()
