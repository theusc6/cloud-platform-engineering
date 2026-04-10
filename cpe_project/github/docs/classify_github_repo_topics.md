# GitHub Repository Classifier

The GitHub Repository Classifier is a script designed to classify repositories within an organization on GitHub based on various criteria, such as intended purpose, subject area, community, or language. The script uses the PyGitHub library to interact with the GitHub API.

## Prerequisites

- Python 3.x installed on your system.
- Required Python packages can be installed using pip:

   ```bash
   pip install PyGithub githubauthlib
   ```

## Usage

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/github-repo-classifier.git
   ```

2. Navigate to the repository directory:

   ```bash
   cd github-repo-classifier
   ```

3. Run the script with the following command:

   ```bash
   python classify_github_repo_topics.py
   ```

## How It Works

The script accesses GitHub repositories within a specified organization and classifies them based on various attributes. The classification includes the following aspects:

- Intended purpose (private/public)
- Subject area (e.g., production, non-production, archive)
- Programming language used

The script fetches repository information using the GitHub API and applies the classification based on predefined rules. The topics associated with a repository are updated to reflect the classification.

## Configuration

Before running the script, make sure to set up your GitHub access token using the `githubauthlib` library. The script retrieves this token to authenticate with the GitHub API. Refer to the [GitHubAuthLib Documentation](https://github.com/KalleDK/githubauthlib) for instructions on how to set up your access token securely.

## Notes

- This script is customized for the "theusc6" organization, but you can modify it for any organization by changing the `ORG_NAME` variable.
- The script uses `PyGithub` library to interact with the GitHub API. Ensure you have the required packages installed.
