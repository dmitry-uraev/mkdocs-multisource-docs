"""Configuration models for the multisource plugin."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class GitLabSourceConfig(BaseModel):
    """GitLab repository source settings."""

    type: Literal["gitlab"]
    host: str
    project_id: int
    token_env: str = "GITLAB_TOKEN"


class GitHubSourceConfig(BaseModel):
    """GitHub repository source settings reserved for the GitHub provider."""

    type: Literal["github"]
    owner: str
    repository: str
    token_env: str = "GITHUB_TOKEN"


class LocalSourceConfig(BaseModel):
    """Local filesystem repository source settings."""

    type: Literal["local"]
    path: str


SourceConfig = Annotated[
    GitLabSourceConfig | GitHubSourceConfig | LocalSourceConfig,
    Field(discriminator="type"),
]


class RepositoryNavigationConfig(BaseModel):
    """Navigation settings for one repository in generated navigation."""

    enabled: bool = True
    title: str | None = None
    index: str | None = None
    include: list[str] = Field(default_factory=list)
    exclude: list[str] = Field(default_factory=list)
    order: int = 0


class NavigationConfig(BaseModel):
    """Global navigation settings."""

    mode: Literal["manual", "auto"] = "manual"
    title: str = "External documentation"
    position: Literal["before", "after"] = "after"


class DocRepository(BaseModel):
    """Documentation repository configuration."""

    name: str
    source: SourceConfig
    branch: str = "main"
    docs_root: str = "."
    web_url: str | None = None
    navigation: RepositoryNavigationConfig = Field(default_factory=RepositoryNavigationConfig)

    # Javadoc
    javadoc: bool = False
    javadoc_command: str | None = None
    javadoc_relative_dir: str | None = None


class AppConfig(BaseModel):
    """Complete plugin configuration."""

    repositories: list[DocRepository] = Field(default_factory=list)
    exclude_images: list[str] = Field(default_factory=list)
    generate_index: bool = False
    navigation: NavigationConfig = Field(default_factory=NavigationConfig)
    link_check: Literal["strict", "warning", "off"] = "warning"

    @property
    def DOCS_REPOSITORIES(self) -> list[DocRepository]:
        """Backward-compatible access for internal processing code."""
        return self.repositories

    @property
    def EXCLUDE_IMAGES(self) -> list[str]:
        """Backward-compatible access for internal processing code."""
        return self.exclude_images

    @property
    def GENERATE_INDEX(self) -> bool:
        """Backward-compatible access for internal processing code."""
        return self.generate_index


def resolve_secret(variable_name: str) -> str:
    """Resolve a secret from the environment, then from a local ``.env`` file."""
    value = os.environ.get(variable_name)
    if value:
        return value

    dotenv_path = Path.cwd() / ".env"
    if dotenv_path.is_file():
        for line in dotenv_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            key, separator, dotenv_value = stripped.partition("=")
            if separator and key.strip() == variable_name:
                return dotenv_value.strip().strip("\"'")

    raise ValueError(f"Secret {variable_name!r} is not set in the environment or {dotenv_path}")


def application_config_from_data(data: dict) -> AppConfig:
    """Parse the inline plugin configuration."""
    return AppConfig.model_validate(data)


def get_demo_application_config() -> AppConfig:
    """Load the repository's demo configuration for standalone module tests."""
    import yaml

    project_root = Path(__file__).resolve().parents[2]
    mkdocs_config_path = project_root / "examples" / "demo" / "mkdocs.yml"
    mkdocs_config = yaml.safe_load(mkdocs_config_path.read_text(encoding="utf-8"))
    plugin_config = next(
        plugin["multisource-docs"]
        for plugin in mkdocs_config["plugins"]
        if isinstance(plugin, dict) and "multisource-docs" in plugin
    )
    return application_config_from_data(plugin_config)


if __name__ == "__main__":
    print(get_demo_application_config().model_dump_json(indent=2))
