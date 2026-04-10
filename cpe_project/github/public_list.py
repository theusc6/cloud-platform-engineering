"""
GitHub Repository Details Viewer
"""
import argparse
from github import Github

def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(
        description='List public GitHub repositories for a specified user.')
    parser.add_argument('-u', '--username', type=str, required=True,
                        help='The name of the GitHub user to search.')
    return parser.parse_args()

def print_repo(repo):
    """
    Print details of a repository
    """
    print("Full name:", repo.full_name)
    print("Description:", repo.description)
    print("Date created:", repo.created_at)
    print("Date of last push:", repo.pushed_at)
    print("Home Page:", repo.homepage)
    print("Language:", repo.language)
    print("Number of forks:", repo.forks)
    print("Number of stars:", repo.stargazers_count)
    print("-" * 50)
    print("Contents:")
    for content in repo.get_contents(""):
        print(content)

def main():
    """
    List public GitHub repositories for a specified user
    """
    args = parse_arguments()
    username = args.username

    # Create a PyGithub object
    git = Github()

    # Get the user by username
    user = git.get_user(username)

    # Print details of all public repositories
    for repo in user.get_repos():
        print_repo(repo)
        print("=" * 50)

if __name__ == '__main__':
    main()
