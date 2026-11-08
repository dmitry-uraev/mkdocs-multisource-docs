# Demo configuration

This page describes only the configuration specific to the runnable demo.
The complete plugin reference is maintained in the root documentation under
`docs/configuration.md`.

## Standalone demo

The demo configures two local repository-like sources in `mkdocs.yml`:

```yaml
plugins:
  - multisource-docs:
      repositories:
        - name: demo-api
          source:
            type: local
            path: sources
          docs_root: docs
        - name: demo-platform
          source:
            type: local
            path: sources
          docs_root: docs
      navigation:
        mode: manual
```

The directories expected by this configuration are:

```text
examples/demo/sources/
├── demo-api/docs/
└── demo-platform/docs/
```

Build the standalone demo from this directory:

```bash
poetry run mkdocs build --clean
```

The root project documentation uses the same source directories with paths
relative to `docs/mkdocs.yml` and includes their practical examples in the
**Demo examples** section.
