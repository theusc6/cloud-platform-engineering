# GitHub Organization Archive Export to AWS S3

This Python script allows you to create an archive of all repositories within a specified GitHub organization and export it to an Amazon Web Services (AWS) S3 bucket. The script uses the GitHub REST API to fetch the repositories, archives them, and then uploads the final archive to S3 for storage.

## Features

- Fetches all repositories from a specified GitHub organization.
- Creates individual archives for each repository using the GitHub archive API.
- Combines individual repository archives into a single final archive.
- Uploads the final archive to an AWS S3 bucket for storage.

## Prerequisites

1. Python 3.x installed.
2. AWS account with an S3 bucket set up.
3. GitHub Personal Access Token with appropriate permissions.

## Usage

1. Clone or download the script to your local machine.
2. Install the required Python packages using pip:

   ```bash
   pip install requests tqdm boto3
   ```

3. Update the script with your GitHub organization name and AWS S3 bucket name.
4. Run the script using the following command:

   ```bash
   python export_org_archive_to_s3.py -p your_aws_profile
   ```

   Replace `your_aws_profile` with your AWS profile name configured for SSO login.

## Script Workflow

1. The script starts by parsing command-line arguments to get the AWS profile name.
2. It fetches a GitHub access token using the `get_github_token()` function.
3. The script then iterates through each page of repositories within the specified GitHub organization.
4. For each repository, it uses the GitHub archive API to create an individual archive in ZIP format.
5. These individual repository archives are then combined into a single final archive.
6. The final archive is uploaded to the specified AWS S3 bucket using the provided AWS profile.
7. Information about the total number of repositories, the number of repositories in the archive, and the upload status is displayed.

## Additional Notes

- The script uses the GitHubAuthLib library to authenticate with the GitHub API.
- Ensure that the S3 bucket exists and is accessible using the provided AWS profile.
- The script utilizes the `requests` library for making HTTP requests and `tqdm` for progress tracking.
- It is recommended to have the necessary AWS and GitHub credentials securely configured before running the script.

## Notes

- This script is customized for the "theusc6" organization, but you can modify it for any organization by changing the `ORG_NAME` variable.
- The script uses `PyGithub` library to interact with the GitHub API. Ensure you have the required packages installed.
