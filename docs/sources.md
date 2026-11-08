# Repository sources

The source provider is selected independently for every repository. The
processing pipeline does not depend on whether the files came from a local
directory or a remote provider.

## Local demo source

The root documentation site uses the local source to collect the two examples
from `examples/demo/sources`:

```yaml
repositories:
  - name: demo-api
    source:
      type: local
      path: examples/demo/sources
    docs_root: docs
```

The resulting pages are visible in the **Demo examples** section of this
site. Their content is practical configuration documentation rather than
placeholder repository text.

## Adding a provider

Providers implement the common repository source contract and can be added
without changing Markdown processing or MkDocs integration. GitHub is the
next planned remote provider.
