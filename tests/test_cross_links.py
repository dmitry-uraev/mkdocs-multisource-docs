import unittest

from mkdocs_multisource_docs.src.config import DocRepository, LocalSourceConfig
from mkdocs_multisource_docs.src.cross_links import (
    resolve_markdown_links,
    resolve_repository_links,
)
from mkdocs_multisource_docs.src.manifest import DocumentManifest


class CrossRepositoryLinksTest(unittest.TestCase):
    def setUp(self):
        self.manifest = DocumentManifest(
            {
                "repo:.docs/guide.html": "/repo/.docs/guide.html",
                "repo:README.md": "/repo/index.html",
                "repo:docs/index.md": "/repo/docs/index.html",
            }
        )

    def test_resolves_reference_and_preserves_anchor(self):
        markdown = '[Guide](fallback){multisource-ref="repo:.docs/guide.html#intro"}'

        result = resolve_markdown_links(
            markdown=markdown,
            source_path="index.md",
            manifest=self.manifest,
            mode="warning",
        )

        self.assertEqual(result, "[Guide](repo/.docs/guide.html#intro)")

    def test_leaves_unannotated_links_unchanged(self):
        markdown = "[Guide](fallback)"

        result = resolve_markdown_links(
            markdown=markdown,
            source_path="index.md",
            manifest=self.manifest,
            mode="warning",
        )

        self.assertEqual(result, markdown)

    def test_preserves_markdown_link_title(self):
        markdown = '[Guide](fallback "Fallback title"){multisource-ref="repo:docs/index.md"}'

        result = resolve_markdown_links(
            markdown=markdown,
            source_path="index.md",
            manifest=self.manifest,
            mode="warning",
        )

        self.assertEqual(result, '[Guide](repo/docs/index.md "Fallback title")')

    def test_resolves_readme_to_mkdocs_source_path(self):
        markdown = '[Repository](fallback){multisource-ref="repo:README.md"}'

        result = resolve_markdown_links(
            markdown=markdown,
            source_path="index.md",
            manifest=self.manifest,
            mode="warning",
        )

        self.assertEqual(result, "[Repository](repo/README.md)")

    def test_redirects_folders_and_non_markdown_files_to_repository(self):
        markdown = (
            "[Folder](../../compiler/groovy/src/test/)\n"
            "[Java](../../sdk/transport/RequestRecord.java)\n"
            "[Markdown](../../docs/guide.md)\n"
            "![Image](../../assets/image.png)"
        )
        repositories = [
            DocRepository(
                name="repo",
                source=LocalSourceConfig(type="local", path="."),
                branch="develop",
                web_url="https://gitlab.example.com/group/repo",
            )
        ]

        result = resolve_repository_links(
            markdown=markdown,
            source_path="repo/modules/transport/Readme.md",
            repositories=repositories,
        )

        self.assertIn(
            "https://gitlab.example.com/group/repo/-/tree/develop/compiler/groovy/src/test",
            result,
        )
        self.assertIn(
            "https://gitlab.example.com/group/repo/-/blob/develop/sdk/transport/RequestRecord.java",
            result,
        )
        self.assertIn("[Markdown](../../docs/guide.md)", result)
        self.assertIn("![Image](../../assets/image.png)", result)

    def test_strict_mode_rejects_missing_target(self):
        with self.assertRaisesRegex(ValueError, "index.md:1"):
            resolve_markdown_links(
                markdown='[Missing](fallback){multisource-ref="repo:missing.md"}',
                source_path="index.md",
                manifest=self.manifest,
                mode="strict",
            )

    def test_warning_mode_keeps_fallback_for_missing_target(self):
        markdown = '[Missing](fallback){multisource-ref="repo:missing.md"}'

        result = resolve_markdown_links(
            markdown=markdown,
            source_path="index.md",
            manifest=self.manifest,
            mode="warning",
        )

        self.assertEqual(result, "[Missing](fallback)")


if __name__ == "__main__":
    unittest.main()
