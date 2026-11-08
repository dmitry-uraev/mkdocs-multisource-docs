"""Common interface for repository sources."""

from pathlib import Path
from typing import Any, Protocol


class RepositorySource(Protocol):
    """Provider-independent repository source contract."""

    def get_repositories(self) -> list[Any]:  # type:ignore
        """Return repositories selected by the application configuration."""

    def clone_repositories(self, repositories: list[Any], clone_path: Path) -> None:
        """Copy or clone repositories into the common build directory."""
