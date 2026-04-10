"""
Fetches all repositories for a given GitHub user.
"""

import argparse
from datetime import datetime
from githubauthlib.github_auth import get_github_token
from github import Github, GithubException

def get_organization(github, organization_name):
    """
    Get the organization from GitHub
    """
    try:
        return github.get_organization(organization_name)
    except GithubException as error:
        print(f"Unable to retrieve the organization '{organization_name}' from GitHub.")
        print(f"Error: {error}")
        raise

def list_repos_for_user(username, org):
    """
    List repositories for a specific user in the organization
    """
    try:
        # Get all repository types in the Organization
        repos = org.get_repos()
        # Get only private repositories
        # repos = org.get_repos(type="private")
    except GithubException as error:
        print(f"Unable to retrieve repositories for user '{username}'.")
        print(f"Error: {error}")
        return

    user_repos = [
        repo
        for repo in repos
        if any(collab.login == username for collab in repo.get_collaborators())
    ]

    if len(user_repos) == 0:
        print(f"No repositories found for user '{username}'.")
    else:
        user_repos.sort(key=lambda repo: repo.name)
        print(f"Found {len(user_repos)} repositories for user '{username}':")
        for repo in user_repos:
            print(repo.name)

def print_completion_message():
    """
    Print the current date, time, and completion message
    """
    now = datetime.now()
    print(f"Script completed successfully on {now.strftime('%Y-%m-%d %H:%M:%S')}.")

def main():
    """
    List private repositories for the defined user in the GitHub organization.
    """
    try:
        # Use the correct keychain for the operating system
        github_token = get_github_token()

        # Create an argument parser
        parser = argparse.ArgumentParser(
            description='List users in a GitHub org that do not have private repositories.')
        parser.add_argument('-o', '--organization', type=str, required=True,
                            help='Your GitHub organization.')
        parser.add_argument('-u', '--user', type=str, required=True,
                            help='Your GitHub username.')
        args = parser.parse_args()

        organization_name = args.organization

        # Create a PyGithub object with the access token
        github = Github(github_token)

        # Get the organization by name
        org = get_organization(github, organization_name)

        # List members without private repositories
        list_repos_for_user(args.user, org)

        # Print the current date and time
        print_completion_message()

    except GithubException as error:
        print(f"An error occurred while communicating with GitHub: {error}")

if __name__ == '__main__':
    main()
