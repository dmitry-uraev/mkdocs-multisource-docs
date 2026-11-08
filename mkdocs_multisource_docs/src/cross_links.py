"""Resolve explicit links between collected documentation repositories."""

from __future__ import annotations

import logging
import posixpath
import re
from pathlib import PurePosixPath
from urllib.parse import quote, urlsplit, urlunsplit

from mkdocs_multisource_docs.src.config import DocRepository
from mkdocs_multisource_docs.src.manifest import DocumentManifest

logger = logging.getLogger(__name__)

_LINK_PATTERN = re.compile(
    r"(?P<prefix>\[[^\]]*\]\()(?P<href>[^)\s]+)"
    r"(?P<title>\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?"
    r"(?P<suffix>\)\{\s*"
    r"multisource-ref\s*=\s*(?P<quote>[\"'])(?P<ref>[^\"']+)"
    r"(?P=quote)\s*\})"
)
_ORDINARY_LINK_PATTERN = re.compile(
    r"(?P<image>!)?(?P<prefix>\[[^\]]*\]\()(?P<href>[^)\s]+)"
    r"(?P<title>\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?"
    r"(?P<suffix>\)(?P<attribute>\{\s*multisource-ref\s*=\s*"
    r"(?:\"[^\"]+\"|'[^']+')\s*\})?)"
)


def resolve_repository_links(
    *,
    markdown: str,
    source_path: str,
    repositories: list[DocRepository],
) -> str:
    """Turn non-Markdown repository links into repository web URLs."""
    repositories_by_name = {repository.name: repository for repository in repositories}
    source_parts = PurePosixPath(source_path).parts
    if not source_parts:
        return markdown
    repository = repositories_by_name.get(source_parts[0])
    if repository is None:
        return markdown
    web_url = repository.web_url
    if not web_url:
        return markdown

    source_relative_path = PurePosixPath(*source_parts[1:]).as_posix()
    source_directory = posixpath.dirname(source_relative_path) or "."

    def replace(match: re.Match[str]) -> str:
        if match.group("image") or match.group("attribute"):
            return match.group(0)

        parsed = urlsplit(match.group("href"))
        if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("/"):
            return match.group(0)
        if parsed.path.lower().endswith(".md"):
            return match.group(0)

        target_path = posixpath.normpath(posixpath.join(source_directory, parsed.path))
        if target_path == ".." or target_path.startswith("../"):
            return match.group(0)

        is_directory = parsed.path.endswith("/") or "." not in PurePosixPath(parsed.path).name
        kind = "tree" if is_directory else "blob"
        repository_url = web_url.rstrip("/")
        target_url = (
            f"{repository_url}/-/"
            f"{kind}/{quote(repository.branch, safe='')}/{quote(target_path, safe='/')}"
        )
        target_url = urlunsplit(("", "", target_url, parsed.query, parsed.fragment))
        return (
            f"{match.group('prefix')}{target_url}"
            f"{match.group('title') or ''}{match.group('suffix')}"
        )

    return _ORDINARY_LINK_PATTERN.sub(replace, markdown)


def resolve_markdown_links(
    *,
    markdown: str,
    source_path: str,
    manifest: DocumentManifest,
    mode: str,
) -> str:
    """Resolve ``multisource-ref`` attributes in Markdown links."""

    def replace(match: re.Match[str]) -> str:
        reference = match.group("ref")
        target, anchor = _split_reference(reference)
        resolved = manifest.documents.get(target)
        line = markdown.count("\n", 0, match.start()) + 1

        if resolved is None:
            message = (
                f"Cross-repository link target {reference!r} was not found "
                f"(source {source_path}:{line})"
            )
            if mode == "strict":
                raise ValueError(message)
            if mode == "warning":
                logger.warning(message)
            return f"{match.group('prefix')}{match.group('href')}{match.group('title') or ''})"

        target_source_path = _target_source_path(target)
        href = _relative_source_path(source_path, target_source_path)
        href += f"#{anchor}" if anchor else ""
        return f"{match.group('prefix')}{href}{match.group('title') or ''})"

    return _LINK_PATTERN.sub(replace, markdown)


def _split_reference(reference: str) -> tuple[str, str | None]:
    """Split a repository path reference into manifest key and anchor."""
    target, separator, anchor = reference.partition("#")
    normalized = PurePosixPath(target).as_posix()
    return normalized, anchor if separator else None


def _target_source_path(target: str) -> str:
    """Convert a manifest key into the source path known by MkDocs."""
    repository, separator, path = target.partition(":")
    if not separator or not repository or not path:
        return target
    return PurePosixPath(repository, path).as_posix()


def _relative_source_path(source_path: str, target_path: str) -> str:
    """Return a target source path relative to the current Markdown page."""
    source_directory = posixpath.dirname(PurePosixPath(source_path).as_posix()) or "."
    return posixpath.relpath(target_path, start=source_directory)
