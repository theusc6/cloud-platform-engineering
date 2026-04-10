#!/usr/bin/env python3

""" 
Get user profile from a GitHub Org
"""

import argparse
import sys
from datetime import datetime
from githubauthlib.github_auth import get_github_token
from github import Github, GithubException

def main():
    """
    Main function
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Show information for a specific user in a GitHub organization.')
    parser.add_argument('-o', '--organization', type=str, required=True,
                        help='The name of the GitHub organization.')
    parser.add_argument('-u', '--username', type=str, required=True,
                        help='The GitHub username to retrieve.')
    args = parser.parse_args()

    # Retrieve GitHub token
    github_token = get_github_token()

    # Create a PyGithub object with the access token
    github = Github(github_token)

    organization_name = args.organization
    username = args.username

    try:
        org = github.get_organization(organization_name)
    except GithubException as error:
        print(f"The {organization_name} organization was NOTFOUND in GitHub.")
        print("Please check your authentication credentials and the organization name.")
        print(f"Error: {error}")
        sys.exit(1)

    # Retrieve user by username within the organization
    user = None
    try:
        for member in org.get_members():
            if member.login == username:
                user = member
                break
        if user is None:
            print(f"{username} was NOTFOUND in {organization_name}.")
            print("Please check your authentication credentials and the username.")
            sys.exit(1)
    except GithubException as error:
        print(f"{username} was NOTFOUND in {organization_name}.")
        print("Please check your authentication credentials and the username.")
        print(f"Error: {error}")
        raise GithubException(error.status, error.data, error.headers) from error

    # Retrieve user's private repositories
    private_repos = []
    try:
        repos = user.get_repos()
        for repo in repos:
            if repo.private:
                private_repos.append(repo.name)
    except GithubException as error:
        print(f"Unable to retrieve repositories for user '{username}'.")
        print(f"Error: {error}")
        sys.exit(1)

    # Print user information
    print(f"Username: {user.login}")
    print(f"Name: {user.name}")
    print(f"Location: {user.location}")
    print(f"Email: {user.email}")
    print(f"Bio: {user.bio}")
    print(f"Company: {user.company}")
    print(f"Private Repositories ({len(private_repos)}):")
    print("-" * 50)
    for repo in private_repos:
        print(f"\t{repo}")

    # Print the current date, time, and completion message
    now = datetime.now()
    print(f"Script completed successfully on {now.strftime('%Y-%m-%d %H:%M:%S')}.")

if __name__ == '__main__':
    main()
