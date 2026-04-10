"""
Classify all repositories in theusc6 with topics that describe their 
intended purpose, subject area, community, or language.
"""

import sys
from githubauthlib.github_auth import get_github_token
from github import Github

def main():
    """
    Main function to classify repositories in theusc6.
    """

    # Use the correct keychain for the operating system
    access_token = get_github_token()

    if access_token is None:
        print("Failed to retrieve GitHub access token. Please check your keychain settings.")
        sys.exit(1)

    # Create a PyGithub instance using the access token
    github_client = Github(access_token)

    # Organization name for private repositories
    org_name = "theusc6"

    classify_repositories(github_client, org_name)

def classify_repositories(client, org_name):
    """
    Classify repositories for the specified user or organization.
    """

    user_or_org_obj = client.get_user(org_name)

    # Iterate over repositories
    for repo in user_or_org_obj.get_repos():
        # Get the existing topics of the repository
        existing_topics = repo.get_topics()

        # Determine the topics based on repository properties
        topics = []

        # Intended purpose
        if org_name == "theusc6":
            topics.append('private')
        else:
            topics.append('public')

        # Subject area
        if 'prod' in repo.name.lower():
            topics.append('production')
        elif 'non-prod' in repo.name.lower():
            topics.append('non-production')
        elif 'archive' in repo.name.lower():
            topics.append('archive')

        # Language
        topics.append(repo.language)

        # Set the new topics for the repository
        repo.replace_topics(topics + existing_topics)

        print(f"Topics set for repository '{repo.name}': {', '.join(topics)}")

    sys.exit(0)

if __name__ == "__main__":
    main()
