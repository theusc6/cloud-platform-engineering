#!/usr/bin/env python3

"""
list gitHub Org users with no repository assignments
"""

import argparse
from datetime import datetime
from githubauthlib.github_auth import get_github_token
from github import Github, GithubException

def main():
    """
    List users in the GitHub organization that do not have any private repository associations.
    """
    try:
        # Use the correct keychain for the operating system
        github_token = get_github_token()

        # Create an argument parser
        parser = argparse.ArgumentParser(
            description='List users in a GitHub org that do not have private repositories.')
        parser.add_argument('-o', '--organization', type=str, required=True,
                            help='Your GitHub organization.')
        args = parser.parse_args()

        organization_name = args.organization

        # Create a PyGithub object with the access token
        github = Github(github_token)

        # Get the organization by name
        org = get_organization(github, organization_name)

        # List members without private repositories
        list_members_without_private_repos(org)

        # Print the current date and time
        print_completion_message()

    except GithubException as error:
        print(f"An error occurred while communicating with GitHub: {error}")

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

def list_members_without_private_repos(org):
    """
    List members without private repositories in the organization
    """
    for member in org.get_members():
        try:
            repos = member.get_repos(type='private')
        except GithubException as error:
            print(f"Unable to retrieve repositories for member '{member.login}'.")
            print(f"Error: {error}")
            continue

        # if the member doesn't have any repositories, print their username
        if repos.totalCount == 0:
            print(member.login)

def print_completion_message():
    """
    Print the current date, time, and completion message
    """
    now = datetime.now()
    print(f"Script completed successfully on {now.strftime('%Y-%m-%d %H:%M:%S')}.")

if __name__ == '__main__':
    main()
