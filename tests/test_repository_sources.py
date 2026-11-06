import tempfile
import unittest
from pathlib import Path

from mkdocs_multisource_docs.src.config import AppConfig, DocRepository
from mkdocs_multisource_docs.src.repository_sources.local import LocalRepositorySource


class LocalRepositorySourceTest(unittest.TestCase):
    def test_copies_configured_repositories_without_network_access(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_root = root / "sources"
            repository_path = source_root / "demo-repo"
            (repository_path / "docs").mkdir(parents=True)
            (repository_path / "docs" / "index.md").write_text("# Demo\n", encoding="utf-8")

            config = AppConfig(
                SOURCE="local",
                LOCAL_SOURCE_PATH="sources",
                DOCS_REPOSITORIES=[
                    DocRepository(
                        name="demo-repo",
                        repo_id=0,
                        branch="demo",
                        docs_root="docs",
                    )
                ],
                EXCLUDE_IMAGES=[],
            )
            source = LocalRepositorySource(config, root)
            destination = root / "build"

            repositories = source.get_repositories()
            source.clone_repositories(repositories, destination)

            self.assertEqual(
                (destination / "demo-repo" / "docs" / "index.md").read_text(encoding="utf-8"),
                "# Demo\n",
            )


if __name__ == "__main__":
    unittest.main()
