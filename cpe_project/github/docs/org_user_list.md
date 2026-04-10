# GitHub Organization User List Script

This script is designed to list all users in a specified GitHub organization, along with statistics about their private repositories and commits made in the past 30 days.

## Requirements

- Python 3.6+
- Required Python packages: `github`, `githubauthlib`, `argparse`

## Usage

1. Make sure you have Python 3.6 or later installed.
2. Install the required packages using the following command:

    ```python
    pip install github githubauthlib argparse
    ```

3. Run the script with the following command:

    ```python
    python script_name.py -o <organization_name>
    ```

    Replace `script_name.py` with the name of the script file and `<organization_name>` with the name of the GitHub organization you want to list users for.

## Features

- Retrieves a list of all users in the specified GitHub organization.
- For each user, calculates the number of private repositories they have and the number of commits made in the past 30 days across those repositories.
- Outputs the collected information for each user.

## Example Output

```bash
Member: user1, Private Repositories: 2, Commits in the past 30 days: 15
Member: user2, Private Repositories: 5, Commits in the past 30 days: 28
...
```

## Notes

- This script is customized for the "theusc6" organization, but you can modify it for any organization by changing the `ORG_NAME` variable.
- The script uses `PyGithub` library to interact with the GitHub API. Ensure you have the required packages installed.

---

Please replace `<organization_name>` with the actual GitHub organization name you want to list users for, and ensure that you have the necessary authentication credentials set up to access the GitHub API.
