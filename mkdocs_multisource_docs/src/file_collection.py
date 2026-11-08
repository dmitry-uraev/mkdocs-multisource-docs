"""Collect documentation pages and resources referenced by them."""

from __future__ import annotations

import re
from collections import deque
from pathlib import Path
from urllib.parse import unquote, urlsplit

from mkdocs_multisource_docs.src.config import AppConfig

_MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(\s*([^\s)]+)")
_HTML_REFERENCE = re.compile(r"(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
_CSS_REFERENCE = re.compile(r"url\(\s*[\"']?([^\"')\s]+)", re.IGNORECASE)
_TEXT_EXTENSIONS = {".css", ".htm", ".html", ".js", ".md", ".mjs", ".svg"}


def collect_repository_files(build_folder: Path, application_config: AppConfig) -> set[Path]:
    """Collect Markdown pages and recursively referenced local resources."""
    build_folder = build_folder.resolve()
    collected: set[Path] = set()

    for repository in application_config.repositories:
        repository_root = (build_folder / repository.name).resolve()
        docs_root = repository_root / repository.docs_root
        if not docs_root.is_dir():
            continue

        pending = deque(
            path
            for path in docs_root.rglob("*.md")
            if path.is_file() and ".git" not in path.relative_to(repository_root).parts
        )
        while pending:
            source_file = pending.popleft()
            if source_file in collected or not source_file.is_file():
                continue
            if not _is_within(source_file, repository_root):
                continue

            collected.add(source_file)
            if source_file.suffix.lower() not in _TEXT_EXTENSIONS:
                continue

            for reference in _references_from(source_file):
                target = _local_target(source_file, reference, repository_root)
                if target is not None and target.is_file() and target not in collected:
                    pending.append(target)

    return collected


def _references_from(source_file: Path) -> list[str]:
    try:
        content = source_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    references = _MARKDOWN_LINK.findall(content)
    references.extend(_HTML_REFERENCE.findall(content))
    if source_file.suffix.lower() == ".css":
        references.extend(_CSS_REFERENCE.findall(content))
    return references


def _local_target(source_file: Path, reference: str, repository_root: Path) -> Path | None:
    parsed = urlsplit(unquote(reference))
    if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("/"):
        return None

    target = (source_file.parent / Path(parsed.path)).resolve()
    if not _is_within(target, repository_root.resolve()):
        return None
    return target


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True
