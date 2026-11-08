# mkdocs-multisource-docs

[![PyPI version](https://img.shields.io/pypi/v/mkdocs-multisource-docs)](https://pypi.org/project/mkdocs-multisource-docs/)
![License](https://img.shields.io/pypi/l/mkdocs-multisource-docs)
![Python versions](https://img.shields.io/pypi/pyversions/mkdocs-multisource-docs)

The `mkdocs-multisource-docs` plugin is designed to automate the process of collecting documentation from multiple repositories and integrating it into the documentation of the current repository. This is particularly useful for projects that rely on documentation spread across multiple repositories, ensuring a unified and up-to-date documentation experience.

## Key Features

- **Multi-repository documentation collection**: automatically fetch and merge documentation from multiple GitLab repositories.
- **Undocumented image documentation generation**: automatically generate documentation for images that lack descriptions.
- **JavaDoc generation**: Automatically generate and include JavaDoc for Java projects.

## Installation

```bash
pip install mkdocs-multisource-docs
```

## Quick Start

Add the plugin to `mkdocs.yml` and configure one repository:

```yaml
plugins:
  - multisource-docs:
      repositories:
        - name: api
          source:
            type: gitlab
            host: https://gitlab.example.com
            project_id: 12345
            token_env: GITLAB_TOKEN
          branch: main
          docs_root: docs
```

Set the token in the environment and build the site:

```bash
export GITLAB_TOKEN=glpat-...
mkdocs build
```

See the [full configuration reference](docs/configuration.md). Build the
repository documentation with:

```bash
poetry run mkdocs build -f docs/mkdocs.yml
```
for local sources, navigation, image handling, and JavaDoc options.

## Configuration

The plugin is configured directly in `mkdocs.yml`:

```yaml
plugins:
  - multisource-docs:
      repositories:
        - name: api
          source:
            type: gitlab
            host: https://gitlab.example.com
            project_id: 12345
            token_env: GITLAB_TOKEN
          branch: main
          docs_root: docs

        - name: local-guide
          source:
            type: local
            path: ./sources
          docs_root: docs

      exclude_images: []
      generate_index: false
      navigation:
        mode: manual
```

Each repository declares its own source, so one site can combine GitLab,
GitHub-compatible future sources, and local directories.

### Secrets

Tokens are referenced by environment variable name and are never stored in
the YAML configuration:

```yaml
token_env: GITLAB_TOKEN
```

The plugin resolves the value from the process environment first and from a
local `.env` file second:

```dotenv
GITLAB_TOKEN=glpat-...
```

Keep `.env` out of version control.

### Navigation

In manual mode, use the standard MkDocs `nav` configuration. The plugin does
not override it:

```yaml
nav:
  - Home: index.md
  - API: api/docs/index.md
  - Platform: platform/docs/index.md
```

In automatic mode, the plugin adds configured repositories to the navigation:

```yaml
plugins:
  - multisource-docs:
      navigation:
        mode: auto
        title: External documentation
        position: after
```

Per-repository navigation options are available in automatic mode:

```yaml
navigation:
  enabled: true
  title: API documentation
  include:
    - "*.md"
  exclude:
    - "internal/**"
  order: 10
```

## Demo and documentation

The repository contains a self-contained documentation site in
[`examples/demo`](examples/demo). It uses two local repository-like sources
and can be built without network access:

```bash
cd examples/demo
poetry run mkdocs build --clean
```

---

## Features in Development

The following features are currently in development and will be available in future releases:

- **Multiple repository tokens**: Support for specifying different access tokens for different repositories.
- **GitHub support**: Extend the plugin to support fetching documentation from GitHub repositories.
- **Enhanced image handling**: Improved support for handling and documenting images.

### Cross-repository links: implementation plan

The first implementation step is complete: after repositories are cloned, the
plugin creates `mt_source_build/.multisource-manifest.json`. For example,
`example-repo:docs/HOWTO/naming_metrics.md` is mapped to
`/example-repo/docs/HOWTO/naming_metrics.html`. The manifest is an intermediate
build artifact and is not copied into the final site; it is an implementation
detail for the future cross-repository link resolver.

The remaining work is planned in the following order:

1. Resolve the plugin configuration path relative to `mkdocs.yml`, and add
   explicit configuration for link checking (`strict`, `warning`, `off`).
2. Parse the optional `multisource-ref="repository:path[#anchor]"` attribute
   on ordinary Markdown links. Replace only `href`, preserve an anchor, and
   remove the service attribute from generated HTML. Links without the
   attribute must remain unchanged, including the GitLab URL fallback.
3. Validate repository and document existence against the manifest, reporting
   the source Markdown file and line number. Apply the configured strict,
   warning, or off behavior.
4. Normalize `.docs/...` paths to `docs/...` in the collected site, preserve
   ordinary relative links inside the current repository, and make navigation
   independent of incidental `.pages` files.
5. Expand copied resource types to include SVG and PDF, then add unit and
   integration coverage for relative links, cross-repository links, anchors,
   missing repositories/files, and disabled-plugin fallback behavior.

And more: Additional features to improve flexibility and usability.

## License

The `mkdocs-multisource-docs` plugin is open-source and can be used freely in any project. However, please provide attribution by linking back to the original repository.

---

Version *2.0.0*

- Breaking: plugin configuration moved from a separate JSON file into `mkdocs.yml`.
- Repository sources are configured independently for each repository.
- GitLab and local sources were separated behind a common repository-source interface.
- Access tokens are resolved securely from environment variables or `.env`.
- Manual and automatic navigation modes were added with repository-level navigation settings.
- A self-contained demo and root documentation site were added.
- Temporary build directories are cleaned up after successful and failed builds.
- Structured colored logging was added, and log messages use lazy formatting.

Version *0.1.3*

- Clonning Git repositories instead of downloading, previous behavior preserved.
- Javadoc additional configuration parameters added into the configuration file: `javadoc_command`, `javadoc_relative_dir`.

Version *0.1.2*

- `GENERATE_INDEX` parameter specifies if plugin should automatically generate index.md file for documentation.
- For each repository in `repositories` the `javadoc` parameter can now be specified to generate Javadoc alongside other docs.
