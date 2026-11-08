# Configuration

The plugin is configured directly in `mkdocs.yml` under `plugins`.

## Minimal configuration

```yaml
plugins:
  - multisource-docs:
      repositories:
        - name: local-guide
          source:
            type: local
            path: ./sources
          docs_root: docs
```

At least one repository is required. The plugin copies each configured source
into the build area, processes its Markdown files, and adds them to the MkDocs
file collection.

## Plugin options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `repositories` | yes | — | Repositories whose documentation should be collected. |
| `exclude_images` | no | `[]` | PNG filenames excluded from generated image documentation. |
| `generate_index` | no | `false` | Generate a root index page listing configured repositories. |
| `navigation` | no | `mode: manual` | Configure generated navigation. |
| `link_check` | no | `warning` | Cross-repository link validation mode: `strict`, `warning`, or `off`. |

## Cross-repository links

Add `multisource-ref` to an ordinary Markdown link to point to a file from a
collected repository:

```markdown
[Naming metrics](https://gitlab.example.com/fallback){multisource-ref="example-repo:docs/HOWTO/naming_metrics.md#overview"}
```

The plugin resolves the reference to the collected source file and preserves
the optional anchor; MkDocs then generates the final site URL. The fallback URL
is used unchanged when the referenced repository or file cannot be resolved in
`warning` or `off` mode. In `strict` mode, an unresolved reference fails the
build. The `multisource-ref` attribute is removed before the final HTML is
generated. As in MkDocs itself,
`README.md` is rendered as `index.html`; reference it as `README.md` in
`multisource-ref`.

## Repository options

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `name` | yes | — | Repository name and output directory name. |
| `source` | yes | — | Source-specific settings. |
| `branch` | no | `main` | Branch for remote sources. Ignored by local sources. |
| `docs_root` | no | `.` | Documentation directory inside the repository. |
| `web_url` | no | `null` | Repository web URL used for folders and non-Markdown file links. |
| `navigation` | no | enabled | Repository settings used by auto navigation. |
| `javadoc` | no | `false` | Enable JavaDoc generation. |
| `javadoc_command` | no | Maven default | Custom JavaDoc command. |
| `javadoc_relative_dir` | no | `null` | Directory from which JavaDoc is generated. |

The plugin initially collects only Markdown files below `docs_root`. It then
adds local files referenced by those pages, such as images, HTML, SVG, PDF, or
JSON resources, including references that resolve outside `docs_root`. Other
repository files are not added to the MkDocs file collection.

When `web_url` is configured, ordinary relative links from collected repository
pages to folders or non-Markdown files are redirected to the repository web
interface. Folders use `/-/tree/<branch>/...`; files use
`/-/blob/<branch>/...`. Markdown links remain internal MkDocs links, and image
links are left unchanged.

## Sources

### GitLab

```yaml
source:
  type: gitlab
  host: https://gitlab.example.com
  project_id: 12345
  token_env: GITLAB_TOKEN
```

`host` and `project_id` identify the project. `token_env` contains the name
of the variable holding the read token; it defaults to `GITLAB_TOKEN`.

### Local

```yaml
source:
  type: local
  path: ./sources
```

The path is relative to the directory containing `mkdocs.yml`. For a
repository named `local-guide`, the expected layout is:

```text
sources/
└── local-guide/
    └── docs/
        └── index.md
```

### GitHub

The configuration shape is reserved for the future GitHub source:

```yaml
source:
  type: github
  owner: company
  repository: platform-docs
  token_env: GITHUB_TOKEN
```

The GitHub provider is not implemented yet.

## Tokens and `.env`

The plugin never expects a token value in `mkdocs.yml`. It resolves tokens in
this order:

1. process environment;
2. `.env` in the current working directory.

Example:

```dotenv
GITLAB_TOKEN=glpat-...
```

The `.env` file should not be committed to the repository.

## Navigation

### Manual mode

Manual mode is the default. The plugin does not modify MkDocs `nav`; the
project's `nav` remains the source of truth:

```yaml
nav:
  - Home: index.md
  - API: api/docs/index.md

plugins:
  - multisource-docs:
      navigation:
        mode: manual
```

Repository navigation settings do not affect the menu in manual mode. The
collected files can be referenced from `nav` explicitly.

### Automatic mode

```yaml
plugins:
  - multisource-docs:
      navigation:
        mode: auto
        title: External documentation
        position: after
```

Global options:

| Option | Default | Description |
| --- | --- | --- |
| `mode` | `manual` | `manual` or `auto`. |
| `title` | `External documentation` | Generated navigation section title. |
| `position` | `after` | Place the generated section before or after existing navigation. |

Per-repository options apply only in auto mode:

```yaml
navigation:
  enabled: true
  title: API documentation
  index: index.md
  include:
    - "*.md"
    - "guide/**"
  exclude:
    - "internal/**"
  order: 10
```

| Option | Default | Description |
| --- | --- | --- |
| `enabled` | `true` | Include the repository in generated navigation. |
| `title` | repository name | Display name in the generated menu. |
| `index` | `index.md` | Landing page relative to `docs_root`. |
| `include` | all Markdown | Glob patterns relative to `docs_root`. |
| `exclude` | `[]` | Glob patterns omitted from navigation. |
| `order` | `0` | Ascending repository order. |

These settings affect navigation only; they do not stop files from being
collected.

## JavaDoc

```yaml
repositories:
  - name: java-api
    source:
      type: gitlab
      host: https://gitlab.example.com
      project_id: 12345
      token_env: GITLAB_TOKEN
      branch: develop
    javadoc: true
    javadoc_command: mvn clean install javadoc:aggregate
    javadoc_relative_dir: sources/java
```

The configured JavaDoc command must be available in the build environment.
Generated documentation is copied to `/apidocs/<repository>/`.
