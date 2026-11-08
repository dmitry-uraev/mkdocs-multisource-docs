# Demo source layout

The demo uses two local repository-like directories:

```text
sources/
├── demo-api/
│   └── docs/
└── demo-platform/
    └── docs/
```

The plugin copies both directories into its build area and makes their
Markdown files available to MkDocs. The root documentation site uses the same
sources, which makes the demo an integration example rather than a mock-only
fixture.
