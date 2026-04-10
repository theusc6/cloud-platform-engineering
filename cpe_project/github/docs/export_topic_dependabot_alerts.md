# GitHub Dependabot Alerts Exporter

This script is designed to fetch tagged Dependabot alerts by Topic from GitHub repositories within a specified organization. It utilizes the GitHub GraphQL API to retrieve information about repositories and their associated security alerts. The alerts are filtered based on repositories that have a specific topic, allowing you to focus on repositories relevant to your use case.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Usage](#usage)
- [Script Flow](#script-flow)
- [Output](#output)

## Prerequisites

Before using this script, make sure you have the following:

- A valid GitHub token to authenticate API requests. You can obtain a token using the `get_github_token()` function from the `githubauthlib` library.
- Python environment with required libraries installed. You can install the necessary libraries using `pip install PyGithub requests githubauthlib`.

## Usage

1. Clone this repository to your local machine.
2. Ensure you have the prerequisites mentioned above.
3. Open a terminal and navigate to the cloned repository directory.
4. Run the script using the following command:

   ```python
   python export_topic_dependabot_alerts.py
   ```

## Script Flow

1. The script starts by configuring the GitHub organization name and API URL.
2. It sets up headers for API requests, including the authorization token.
3. The script initiates a GraphQL query to fetch all repositories within the organization.
4. Pagination is used to retrieve repositories in batches of 100.
5. For each repository, the script checks if it has a specific topic (e.g., 'production-code').
6. If the repository has the specified topic, another GraphQL query is used to fetch Dependabot alerts for that repository.
7. The script collects information about each alert, such as package name, vulnerability severity, timestamps, etc.
8. The collected alert data is stored in a list for further processing.
9. The script counts the number of repositories with alerts and the count of alerts for each repository.
10. An output CSV file is generated containing the alert information for repositories with the specified topic.

## Output

The script generates a CSV file named `dependabot_alerts_timestamp.csv`, where `timestamp` is the date and time when the script was executed. The CSV file includes the following columns:

- `repository`: Repository name
- `alert_id`: Alert ID
- `package_name`: Name of the vulnerable package
- `vulnerableManifestPath`: Path to the vulnerable manifest file
- `vulnerableRequirements`: Vulnerable requirements information
- `vulnerability_severity`: Severity of the vulnerability
- `created_at`: Timestamp when the alert was created
- `updated_at`: Timestamp when the alert was last updated
- `dismissed_at`: Timestamp when the alert was dismissed (if applicable)
- `topics`: List of repository topics

The script also provides console output regarding the progress of fetching repositories and alerts.

---

## Notes

- This script is customized for the "theusc6" organization, but you can modify it for any organization by changing the `ORG_NAME` variable.
- The script uses `PyGithub` library to interact with the GitHub API. Ensure you have the required packages installed.
