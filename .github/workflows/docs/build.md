# GitHub Actions Workflow: SonarCloud Scan

This GitHub Actions workflow is designed to automate the process of running a SonarCloud scan on your codebase when changes are pushed to the `main` branch or a pull request is opened, synchronized, or reopened.

## Purpose

The main purpose of this workflow is to perform code analysis using SonarCloud, which provides insights into code quality, security vulnerabilities, and code smells. By integrating SonarCloud into your development process, you can identify and address issues early, ensuring that your codebase meets high standards of maintainability and security.

## Workflow Steps

1. **Checkout Code:**
   The workflow starts by checking out the code repository using the `actions/checkout` action. This step ensures that the latest code changes are available for analysis.

2. **SonarCloud Scan:**
   After checking out the code, the workflow uses the `SonarSource/sonarcloud-github-action` action to run a SonarCloud scan on the codebase. This action analyzes the code, generates insights, and provides a comprehensive report on code quality, security issues, and more.

## Triggers

The workflow is triggered by two events:

- Push to `main` Branch:
  Whenever code changes are pushed to the `main` branch, the workflow is triggered to perform a SonarCloud scan on the latest code.

- Pull Request:
  The workflow is also triggered when a pull request is opened, synchronized, or reopened. This ensures that code changes submitted through pull requests undergo analysis before they are merged.

## Environment Variables

The following environment variables are used in the workflow:

- `GITHUB_TOKEN`:
  This token is provided by GitHub and is used to authenticate actions performed within the GitHub environment. It is required to fetch PR information for the SonarCloud scan.

- `SONAR_TOKEN`:
  This token is provided by SonarCloud and is used to authenticate the SonarCloud scan. It allows the scan results to be uploaded to the SonarCloud dashboard.

## Conclusion

By using this GitHub Actions workflow, you can automate the process of analyzing your codebase for quality and security issues through SonarCloud scans. This helps maintain a high level of code quality, improve security, and identify areas for code improvement. Additionally, the workflow's integration with pull requests ensures that code changes are thoroughly assessed before merging into the `main` branch.

**Note:** Make sure to configure the required secrets (`GITHUB_TOKEN` and `SONAR_TOKEN`) in your repository settings to enable the successful execution of this workflow.
