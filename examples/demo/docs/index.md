# Demo project

This directory is a runnable example project for `mkdocs-multisource-docs`.
Its configuration is in `mkdocs.yml`, and its two repository-like sources are
in `sources/`.

The root project documentation builds the same sources through the plugin.
The pages under `docs/` explain the demo scenarios; the pages under
`sources/` are the documentation that the plugin collects.

Build this project independently with:

```bash
poetry run mkdocs build --clean
```

See the [demo configuration](configuration.md) and the [source layout](sources.md)
for the details.
