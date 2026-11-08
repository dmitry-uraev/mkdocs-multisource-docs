# GitLab source configuration

This page is collected into the root documentation site from the second demo
source. A remote GitLab repository uses the same repository-level structure:

```yaml
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

The token is resolved from the environment or `.env`; it is never stored in
the MkDocs configuration.
