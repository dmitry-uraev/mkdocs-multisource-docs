# Repository sources

The plugin separates repository access from documentation processing.

The demo uses the local source. Each configured repository is represented by a
directory under `sources/`, and its contents are copied into the build before
MkDocs processes the files.

In a production project the same stage can fetch repositories from GitLab.
Additional providers, such as GitHub, can use the same source interface while
leaving the rest of the documentation pipeline unchanged.
