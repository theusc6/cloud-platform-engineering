"""
A script that lists all users on a GitHub Enterprise server.
"""

import subprocess
import json
import sys
import re

def get_all_users(per_page=100):
    """
    A function that returns a list of all users on a GitHub Enterprise server.
    """
    all_users = []
    page = 1

    while True:
        # Execute the gh command to get user information for each page
        users_command = ["gh", "api", f"/users?per_page={per_page}&page={page}"]
        users_output = subprocess.run(users_command, capture_output=True, text=True, check=True)

        if users_output.returncode != 0:
            print("Failed to retrieve user information.")
            print("Error:", users_output.stderr)
            break

        response_json = json.loads(users_output.stdout)
        all_users.extend(response_json)

        # Check for the presence of a "next" link in the pagination
        links = parse_link_header(users_output.stdout)
        if "next" not in links:
            break

        page += 1

    return all_users

def parse_link_header(header):
    """
    A function that parses the Link header returned by the GitHub API.
    """
    links = {}
    parts = header.split(", ")

    for part in parts:
        section = part.split("; ")
        url = section[0][1:-1]
        real_name = re.search(r'rel="(.*)"', section[1]).group(1) if len(section) > 1 else None

        if real_name:
            links[real_name] = url

    return links

try:
    # Get all users
    all_users_list = get_all_users()
    TOTAL_USERS = len(all_users_list)
    print(f"Total Users: {TOTAL_USERS}\n")

    # Extract user information for all users
    for user in all_users_list:
        username = user["login"]
        # Execute the gh command to get user information for each user
        user_info_command = ["gh", "api", f"/users/{username}"]
        user_info_output = subprocess.run(user_info_command, capture_output=True, text=True, check=True)

        if user_info_output.returncode != 0:
            print(f"Failed to retrieve user information for {username}.")
            print("Error:", user_info_output.stderr)
            continue

        user_info_json = json.loads(user_info_output.stdout)
        name = user_info_json.get("name", "N/A")
        email = user_info_json.get("email", "N/A")
        public_repos = user_info_json.get("public_repos", "N/A")
        created_at = user_info_json.get("created_at", "N/A")
        print(f"User Information for {username}:")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Public Repositories: {public_repos}")
        print(f"Account Created At: {created_at}")
        print("\n" + "-" * 50 + "\n")

except subprocess.CalledProcessError as error:
    print("Error occurred while retrieving user information:", error)
except KeyboardInterrupt:
    sys.exit(0)
