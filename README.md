# mkdocs-multisource-docs

The `mkdocs-multisource-docs` plugin is designed to automate the process of collecting documentation from multiple GitLab repositories and integrating it into the documentation of the current repository. This is particularly useful for projects that rely on documentation spread across multiple repositories, ensuring a unified and up-to-date documentation experience.

## Key Features

- **Multi-repository documentation collection**: automatically fetch and merge documentation from multiple GitLab repositories.
- **Undocumented image documentation generation**: automatically generate documentation for images that lack descriptions.
- **Seamless integration**: easily integrate with MkDocs to enhance your documentation workflow.

---

## Quick Start

1. Install the plugin:

   Install the plugin using pip:

    ```bash
    pip install mkdocs_multisource_docs
    ```

2. Add the plugin to your `mkdocs.yml`:

   Include the plugin in your MkDocs configuration file and specify the path to the configuration file:

    ```yaml
    plugins:
      - multisource-docs:
          multisource_config: "./application.json"
    ```

3. Configure the `application.json` file:

   Create a configuration file (`application.json`) to specify the GitLab host, token, and repositories to fetch documentation from. See the configuration details below.

### Configuration File Parameters

The `application.json` file is used to configure the plugin. Below is a table describing all the required parameters:

| Parameter         | Description                                                         | Example Value                |
|-------------------|---------------------------------------------------------------------|------------------------------|
| GIT_HOST          | The GitLab host URL.                                                | "https://gitlab.example.com" |
| GIT_READ_TOKEN    | A GitLab access token with read permissions for the repositories.   | "glpat-xxxxxxxxxxxxxxxxxxxx" |
| DOCS_REPOSITORIES | A list of repositories to fetch documentation from.                 | See below for structure      |
| EXCLUDE_IMAGES    | (Optional) A list of image filenames to exclude from documentation. | ["image1.png", "image2.png"] |

#### DOCS_REPOSITORIES Structure

The `DOCS_REPOSITORIES` parameter is a list of objects, each representing a repository. Each object has the following fields:

| Field   | Description                                               | Example Value |
|---------|-----------------------------------------------------------|---------------|
| name    | The name of the repository.                               | "my-repo"     |
| repo_id | The ID of the repository.                                 | 12345         |
| branch  | The branch of the repository to fetch documentation from. | "main"        |

**Example application.json**

```json
{
    "GIT_HOST": "https://gitlab.example.com",
    "GIT_READ_TOKEN": "glpat-xxxxxxxxxxxxxxxxxxxx",
    "DOCS_REPOSITORIES": [
        {
            "name": "my-repo-1",
            "repo_id": 12345,
            "branch": "main"
        },
        {
            "name": "my-repo-2",
            "repo_id": 67890,
            "branch": "dev"
        }
    ],
    "EXCLUDE_IMAGES": [
        "logo.png",
        "example.png"
    ]
}
```

---

## Features in Development

The following features are currently in development and will be available in future releases:

- **Multiple repository tokens**: Support for specifying different access tokens for different repositories.
- **JavaDoc generation**: Automatically generate and include JavaDoc for Java projects.
- **GitHub support**: Extend the plugin to support fetching documentation from GitHub repositories.
- **Enhanced image handling**: Improved support for handling and documenting images.

And more: Additional features to improve flexibility and usability.

## License

The `mkdocs-multisource-docs` plugin is open-source and can be used freely in any project. However, please provide attribution by linking back to the original repository.

---

For more information, issues, or contributions, please visit the GitHub repository.
