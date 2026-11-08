# Automatic navigation configuration

This page demonstrates generated navigation. Set the global mode to `auto`
and configure the repository entry:

```yaml
plugins:
  - multisource-docs:
      repositories:
        - name: demo-api
          source:
            type: local
            path: sources
          docs_root: docs
          navigation:
            enabled: true
            title: API examples
            index: index.md
            include:
              - "*.md"
            order: 10
      navigation:
        mode: auto
        title: External documentation
        position: after
```

In manual mode, the project's regular MkDocs `nav` configuration remains the
source of truth.
