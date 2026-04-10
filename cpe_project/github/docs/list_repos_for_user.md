GitHub Copilot: # GitHub User Repositories Fetcher

This Python script fetches all repositories for a given GitHub user. It uses the PyGithub library to interact with the GitHub API and requires authentication using a GitHub access token.

## Usage

1. Clone the repository to your local machine.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Run the script using the following command:

   ```python
   python list_repos_for_user.py -u <username> -o <organization>
   ```

   Replace `<username>` with the GitHub username and `<organization>` with the name of the GitHub organization.

   For example:

   ```python
   python list_repos_for_user.py -u user -o theusc6
   ```

4. The script will list all private repositories for the specified user in the organization. If no repositories are found, it will print a message indicating that no repositories were found. Finally, it will print the current date and time to indicate that the script has completed successfully.

## Requirements

- Python 3.x
- PyGithub library
- argparse library

## Notes

- This script is customized for the "theusc6" organization, but you can modify it for any organization by changing the `organization` argument.
- The script uses `PyGithub` library to interact with the GitHub API. Ensure you have the required packages installed.
