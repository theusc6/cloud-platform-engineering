# BADGES.md

## Creating GitHub Badges for Build Jobs

GitHub badges serve as a visual representation of the build status, code quality, and other CI/CD-related metrics for your repositories. They provide a quick way to convey the current status of your codebase to developers and other stakeholders. This guide explains how to create GitHub badges for Sonarcloud build jobs and Python status from GitHub Actions workflow files.

### Prerequisites

- A GitHub repository with GitHub Actions enabled.
- Configured build jobs in your GitHub Actions workflows.
- A Sonarcloud account with your project setup and integrated with your GitHub repository.

### Creating a GitHub Badge

A GitHub badge for a workflow is generated using a specific URL pattern. Below are examples for a Sonarcloud build job and a Python status badge:

#### 1. Sonarcloud Status Badge:

Markdown Code:
```markdown
![Sonarcloud status](https://github.com/<username>/<repository>/actions/workflows/<workflow_file>.yaml/badge.svg?event=push)
```

Replace `<username>`, `<repository>`, and `<workflow_file>` with your GitHub username, repository name, and the name of your workflow file respectively.

Example:
```markdown
![Sonarcloud status](https://github.com/theusc6/cloud-platform-engineering/actions/workflows/build.yaml/badge.svg?event=push)
```

This will generate a badge like this: ![Sonarcloud status](https://github.com/theusc6/cloud-platform-engineering/actions/workflows/build.yaml/badge.svg?event=push)

#### 2. Python Status Badge:

Markdown Code:
```markdown
![Python status](https://github.com/<username>/<repository>/actions/workflows/<workflow_file>.yaml/badge.svg?event=push)
```

Replace `<username>`, `<repository>`, and `<workflow_file>` with your GitHub username, repository name, and the name of your workflow file respectively.

Example:
```markdown
![Python status](https://github.com/theusc6/cloud-platform-engineering/actions/workflows/pylint.yaml/badge.svg?event=push)
```

This will generate a badge like this: ![Python status](https://github.com/theusc6/cloud-platform-engineering/actions/workflows/pylint.yaml/badge.svg?event=push)

### Embedding Badges in Your README.md

You can embed these badges directly into your `README.md` file or any other Markdown file in your repository by simply pasting the Markdown code where you want the badge to appear.

Example:
```markdown
# cloud-platform-engineering

![Sonarcloud status](https://github.com/theusc6/cloud-platform-engineering/actions/workflows/build.yaml/badge.svg?event=push)
![Python status](https://github.com/theusc6/cloud-platform-engineering/actions/workflows/pylint.yaml/badge.svg?event=push)
```

This will display the badges at the top of your project's README file, providing a quick overview of the build status.

### Conclusion

GitHub badges are a powerful tool for communicating the status of your build jobs and code quality metrics. By following the steps outlined in this guide, you can easily create and embed these badges in your repository, enhancing transparency and accountability in your development process.