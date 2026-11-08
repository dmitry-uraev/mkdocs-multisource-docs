# Local source configuration

This page is collected into the root documentation site from the local
`demo-api` source.

Use a local source when documentation is available in a directory on disk:

```yaml
plugins:
  - multisource-docs:
      repositories:
        - name: demo-api
          source:
            type: local
            path: examples/demo/sources
          docs_root: docs
```

The directory below `path` must have the repository name:

```text
examples/demo/sources/demo-api/docs/index.md
```

The same configuration is used by both the standalone demo and the root
documentation site.
