# List GitHub Organization Members Without Private Repositories

This script is designed to list the members of a GitHub organization who do not have any private repository associations. It utilizes the GitHub API to fetch organization members and their repository information to determine if they have any private repositories.

## Prerequisites

Before using this script, make sure you have the following:

1. Python environment set up with required dependencies (you can refer to the `requirements.txt` file).
2. GitHub authentication token configured using the `githubauthlib.github_auth` module.
3. Access to the GitHub organization you want to analyze.

## Usage

1. Run the script by executing the following command in your terminal:

    ```sh
    python script_name.py -o organization_name
    ```

    Replace `script_name.py` with the actual name of your script file and `organization_name` with the name of the GitHub organization you want to analyze.

2. The script will fetch members of the specified organization and check if they have any private repositories associated. If a member does not have any private repositories, their username will be displayed in the terminal.

3. The script will also print the current date, time, and a completion message.

## Example

```sh
python org_user_with_no_repos.py -o theusc6
```

## Notes

- This script is customized for the "theusc6" organization, but you can modify it for any organization by changing the `ORG_NAME` variable.
- The script uses `PyGithub` library to interact with the GitHub API. Ensure you have the required packages installed.
