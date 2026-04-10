# GitHub Organization User Profile Information

This script is designed to fetch and display detailed user profile information from a GitHub organization. It uses the PyGithub library to interact with the GitHub API and retrieve relevant data about a specific user within the organization.

## Purpose

The main purpose of this script is to provide an easy way to retrieve and display user profile information from a GitHub organization. It helps you quickly access details such as username, name, location, email, bio, company, and a list of private repositories associated with the user.

## How to Use

1. Make sure you have Python installed on your system.
2. Install the required libraries using the following command:

    ```python
    pip install PyGithub argparse githubauthlib
    ```

3. Run the script with the following command:

    ```python
    python get_user_profile.py -o <organization_name> -u <username>
    ```

    Replace `<organization_name>` with the name of the GitHub organization and `<username>` with the GitHub username you want to retrieve information for.

## Features

- Fetches detailed profile information of a specific user within a GitHub organization.
- Retrieves and displays user's name, location, email, bio, company, and private repositories.

## Requirements

- Python 3.x
- PyGithub library (`pip install PyGithub`)
- githubauthlib library (`pip install githubauthlib`)

## Example

To fetch and display user profile information for the user "john_doe" in the organization "Labz," use the following command:

```python
python get_user_profile.py -o theusc6 -u user
```

## Notes

- This script is customized for the "theusc6" organization, but you can modify it for any organization by changing the `ORG_NAME` variable.
- The script uses `PyGithub` library to interact with the GitHub API. Ensure you have the required packages installed.
