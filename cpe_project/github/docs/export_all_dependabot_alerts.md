# GitHub Dependabot Alerts Export Script

This Python script is designed to automate the retrieval of Dependabot alerts from multiple repositories within a GitHub organization and export them to a CSV file. It leverages the GitHub GraphQL API to fetch the list of repositories and their associated vulnerability alerts. The collected data is then organized and exported to a CSV file for further analysis.

## Features

- Fetches repositories and associated Dependabot alerts from a specified GitHub organization.
- Utilizes the GitHub GraphQL API for efficient data retrieval.
- Exports the collected alert data to a CSV file for easy review and analysis.

## Prerequisites

1. Python 3.x installed.
2. GitHub Personal Access Token with appropriate permissions.
3. Required Python packages: `requests`, `csv`.

## Usage

1. Clone or download the script to your local machine.
2. Install the required Python packages using pip:

   ```bash
   pip install requests
   ```

3. Update the script with your GitHub organization name and GitHub Personal Access Token.
4. Run the script using the following command:

   ```bash
   python script_name.py
   ```

   Replace `script_name.py` with the actual name of the script file.

## Script Workflow

1. The script starts by importing the necessary modules and setting up the GitHub API URL and headers.
2. It retrieves the GitHub access token using the `get_github_token()` function from the GitHubAuthLib library.
3. The script fetches a list of repositories within the specified GitHub organization using a GraphQL query.
4. For each repository, it then queries the GraphQL API to retrieve the associated Dependabot alerts.
5. The fetched alerts data is structured into a list of dictionaries for further processing.
6. The script creates a CSV file and writes the fetched alert data to it in tabular format.
7. The CSV file is saved with a timestamp to avoid overwriting existing files.
8. Information about the exported alerts and the CSV file's location is displayed.

## Additional Notes

- Ensure that the GitHub Personal Access Token has the necessary permissions to access the repositories and vulnerability alerts.
- The script leverages the GitHubAuthLib library for token authentication.
- It uses the `requests` library to make HTTP requests to the GitHub GraphQL API.
- The exported CSV file contains information about repository name, alert details, timestamps, and more.

## Notes

- This script is customized for the "theusc6" organization, but you can modify it for any organization by changing the `ORG_NAME` variable.
- The script uses `PyGithub` library to interact with the GitHub API. Ensure you have the required packages installed.
