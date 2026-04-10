# BADGES.md

## Creating GitHub Badges for Build Jobs

GitHub badges serve as a visual representation of the build status, code quality, and other CI/CD-related metrics for your repositories. They provide a quick way to convey the current status of your codebase to developers and other stakeholders.

### Prerequisites

- A GitHub repository with GitHub Actions enabled.
- Configured build jobs in your GitHub Actions workflows.

### Creating a GitHub Badge

A GitHub badge for a workflow is generated using a specific URL pattern:

```markdown
![Badge Name](https://github.com/<username>/<repository>/actions/workflows/<workflow_file>.yaml/badge.svg?event=push)
```

Replace `<username>`, `<repository>`, and `<workflow_file>` with your GitHub username, repository name, and the name of your workflow file respectively.

#### Example: Pylint Status Badge

```markdown
![Pylint](https://github.com/theusc6/cloud-platform-engineering/actions/workflows/pylint.yaml/badge.svg?event=push)
```

This will generate a badge like this: ![Pylint](https://github.com/theusc6/cloud-platform-engineering/actions/workflows/pylint.yaml/badge.svg?event=push)

### Embedding Badges in Your README.md

Paste the Markdown code at the top of your `README.md`:

```markdown
# cloud-platform-engineering

![Pylint](https://github.com/theusc6/cloud-platform-engineering/actions/workflows/pylint.yaml/badge.svg?event=push)
```

### Conclusion

GitHub badges are a powerful tool for communicating the status of your build jobs and code quality metrics. By following the steps outlined in this guide, you can easily create and embed these badges in your repository.