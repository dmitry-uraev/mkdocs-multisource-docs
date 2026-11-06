# Configuration

The plugin is enabled in `mkdocs.yml`:

```yaml
plugins:
  - multisource-docs:
      multisource_config: application.local.json
```

The application configuration describes the repositories that should be
included in the site:

```json
{
  "SOURCE": "local",
  "LOCAL_SOURCE_PATH": "sources",
  "DOCS_REPOSITORIES": [
    {
      "name": "demo-api",
      "repo_id": 0,
      "branch": "demo",
      "docs_root": "docs"
    }
  ],
  "EXCLUDE_IMAGES": [],
  "GENERATE_INDEX": false
}
```

For a GitLab project, omit `SOURCE` or set it to `gitlab`, then provide
`GIT_HOST`, `GIT_READ_TOKEN`, and the GitLab repository IDs. The remaining
Markdown processing is the same for both sources.
