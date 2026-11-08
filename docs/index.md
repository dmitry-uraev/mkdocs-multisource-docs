# mkdocs-multisource-docs

`mkdocs-multisource-docs` collects Markdown documentation from multiple
repositories and publishes it as one MkDocs site.

This documentation is built by the plugin itself. The pages in **Demo
examples** are collected from the local repository-like directories in
`examples/demo/sources`, so the site is also an end-to-end example of the
plugin configuration.

## What the plugin does

- collects documentation from configured repository sources;
- supports a different source configuration for every repository;
- adds collected Markdown and assets to the MkDocs build;
- optionally generates pages for undocumented PNG images;
- optionally generates JavaDoc;
- supports manual and automatic navigation.

Start with the [configuration reference](configuration.md), then inspect the
[repository sources](sources.md) and the collected demo examples.
